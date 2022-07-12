from __future__ import annotations

import logging
import json
import time
import dataclasses
from operator import attrgetter
from typing import Any, Optional, Tuple, Set, List, Dict, Type, TypeVar, TYPE_CHECKING

from blspy import G2Element

from chia.consensus.block_record import BlockRecord
from chia.protocols.wallet_protocol import PuzzleSolutionResponse, CoinState
from chia.wallet.db_wallet.db_wallet_puzzles import (
    ACS_MU,
    ACS_MU_PH,
    create_host_fullpuz,
    SINGLETON_LAUNCHER,
    create_host_layer_puzzle,
    launch_solution_to_singleton_info,
    match_dl_singleton,
)
from chia.types.announcement import Announcement
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.program import Program, SerializedProgram
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_spend import CoinSpend
from chia.types.condition_opcodes import ConditionOpcode
from chia.types.spend_bundle import SpendBundle
from chia.util.ints import uint8, uint32, uint64, uint128
from chia.util.json_util import dict_to_json_str
from chia.util.streamable import Streamable, streamable
from chia.wallet.derivation_record import DerivationRecord
from chia.wallet.sign_coin_spends import sign_coin_spends
from chia.wallet.transaction_record import TransactionRecord
from chia.wallet.wallet_coin_record import WalletCoinRecord
from chia.wallet.lineage_proof import LineageProof
from chia.wallet.util.compute_memos import compute_memos
from chia.wallet.util.transaction_type import TransactionType
from chia.wallet.util.wallet_types import AmountWithPuzzlehash, WalletType
from chia.wallet.wallet import Wallet
from chia.wallet.wallet_info import WalletInfo

if TYPE_CHECKING:
    from chia.wallet.wallet_state_manager import WalletStateManager


@streamable
@dataclasses.dataclass(frozen=True)
class SingletonRecord(Streamable):
    coin_id: bytes32
    launcher_id: bytes32
    root: bytes32
    inner_puzzle_hash: bytes32
    confirmed: bool
    confirmed_at_height: uint32
    lineage_proof: LineageProof
    generation: uint32
    timestamp: uint64


_T_DataLayerWallet = TypeVar("_T_DataLayerWallet", bound="DataLayerWallet")


class DataLayerWallet:
    wallet_state_manager: WalletStateManager
    log: logging.Logger
    wallet_info: WalletInfo
    wallet_id: uint8
    standard_wallet: Wallet
    """
    interface used by datalayer for interacting with the chain
    """

    @classmethod
    async def create(
        cls: Type[_T_DataLayerWallet],
        wallet_state_manager: WalletStateManager,
        wallet: Wallet,
        wallet_info: WalletInfo,
        name: Optional[str] = None,
    ) -> _T_DataLayerWallet:
        self = cls()
        self.wallet_state_manager = wallet_state_manager
        self.log = logging.getLogger(name if name else __name__)
        self.standard_wallet = wallet
        self.wallet_info = wallet_info
        self.wallet_id = uint8(self.wallet_info.id)

        return self

    @classmethod
    def type(cls) -> uint8:
        return uint8(WalletType.DATA_LAYER)

    def id(self) -> uint32:
        return self.wallet_info.id

    @classmethod
    async def create_new_dl_wallet(
        cls: Type[_T_DataLayerWallet],
        wallet_state_manager: WalletStateManager,
        wallet: Wallet,
        name: Optional[str] = "DataLayer Wallet",
        in_transaction: bool = False,
    ) -> _T_DataLayerWallet:
        """
        This must be called under the wallet state manager lock
        """

        self = cls()
        self.wallet_state_manager = wallet_state_manager
        self.log = logging.getLogger(name if name else __name__)
        self.standard_wallet = wallet

        for _, wallet in self.wallet_state_manager.wallets.items():
            if wallet.type() == uint8(WalletType.DATA_LAYER):
                raise ValueError("DataLayer Wallet already exists for this key")

        assert name is not None
        maybe_wallet_info = await wallet_state_manager.user_store.create_wallet(
            name,
            WalletType.DATA_LAYER.value,
            "",
            in_transaction=in_transaction,
        )
        if maybe_wallet_info is None:
            raise ValueError("Internal Error")
        self.wallet_info = maybe_wallet_info
        self.wallet_id = uint8(self.wallet_info.id)

        await self.wallet_state_manager.add_new_wallet(self, self.wallet_info.id, in_transaction=in_transaction)

        return self

    #############
    # LAUNCHING #
    #############

    @staticmethod
    async def match_dl_launcher(launcher_spend: CoinSpend) -> Tuple[bool, Optional[bytes32]]:
        # Sanity check it's a launcher
        if launcher_spend.puzzle_reveal.to_program() != SINGLETON_LAUNCHER:
            return False, None

        # Let's make sure the solution looks how we expect it to
        try:
            full_puzhash, amount, root, inner_puzhash = launch_solution_to_singleton_info(
                launcher_spend.solution.to_program()
            )
        except ValueError:
            return False, None

        # Now let's check that the full puzzle is an odd data layer singleton
        if (
            full_puzhash != create_host_fullpuz(inner_puzhash, root, launcher_spend.coin.name()).get_tree_hash(inner_puzhash)
            or amount % 2 == 0
        ):
            return False, None

        return True, inner_puzhash

    async def get_launcher_coin_state(self, launcher_id: bytes32) -> CoinState:
        coin_states: List[CoinState] = await self.wallet_state_manager.wallet_node.get_coin_state([launcher_id])

        if len(coin_states) == 0:
            raise ValueError(f"Launcher ID {launcher_id} is not a valid coin")
        if coin_states[0].coin.puzzle_hash != SINGLETON_LAUNCHER.get_tree_hash():
            raise ValueError(f"Coin with ID {launcher_id} is not a singleton launcher")
        if coin_states[0].created_height is None:
            raise ValueError(f"Launcher with ID {launcher_id} has not been created (maybe reorged)")
        if coin_states[0].spent_height is None:
            raise ValueError(f"Launcher with ID {launcher_id} has not been spent")

        return coin_states[0]

    async def track_new_launcher_id(  # This is the entry point for non-owned singletons
        self,
        launcher_id: bytes32,
        spend: Optional[CoinSpend] = None,
        height: Optional[uint32] = None,
        in_transaction: bool = False,
    ) -> None:
        if await self.wallet_state_manager.dl_store.get_launcher(launcher_id) is not None:
            self.log.info(f"Spend of launcher {launcher_id} has already been processed")
            return None
        if spend is not None and spend.coin.name() == launcher_id:  # spend.coin.name() == launcher_id is a sanity check
            await self.new_launcher_spend(spend, height, in_transaction)
        else:
            launcher_state: CoinState = await self.get_launcher_coin_state(launcher_id)

            data: Dict[str, Any] = {
                "data": {
                    "action_data": {
                        "api_name": "request_puzzle_solution",
                        "height": launcher_state.spent_height,
                        "coin_name": launcher_id,
                        "launcher_coin": {
                            "parent_id": launcher_state.coin.parent_coin_info.hex(),
                            "puzzle_hash": launcher_state.coin.puzzle_hash.hex(),
                            "amount": str(launcher_state.coin.amount),
                        },
                    }
                }
            }

            data_str = dict_to_json_str(data)
            await self.wallet_state_manager.create_action(
                name="request_puzzle_solution",
                wallet_id=self.id(),
                wallet_type=self.type(),
                callback="new_launcher_spend_response",
                done=False,
                data=data_str,
                in_transaction=False,  # We should never be fetching this during sync, it will provide us with the spend
            )

    async def new_launcher_spend_response(self, response: PuzzleSolutionResponse, action_id: int) -> None:
        action = await self.wallet_state_manager.action_store.get_wallet_action(action_id)
        assert action is not None
        coin_dict = json.loads(action.data)["data"]["action_data"]["launcher_coin"]
        launcher_coin = Coin(
            bytes32.from_hexstr(coin_dict["parent_id"]),
            bytes32.from_hexstr(coin_dict["puzzle_hash"]),
            uint64(int(coin_dict["amount"])),
        )
        await self.new_launcher_spend(
            CoinSpend(launcher_coin, response.puzzle, response.solution),
            height=response.height,
        )

    async def new_launcher_spend(
        self,
        launcher_spend: CoinSpend,
        height: Optional[uint32] = None,
        in_transaction: bool = False,
    ) -> None:
        launcher_id: bytes32 = launcher_spend.coin.name()
        if height is None:
            height = (await self.get_launcher_coin_state(launcher_id)).spent_height
            assert height is not None
        full_puzhash, amount, root, inner_puzhash = launch_solution_to_singleton_info(
            launcher_spend.solution.to_program()
        )
        new_singleton = Coin(launcher_id, full_puzhash, amount)

        singleton_record: Optional[SingletonRecord] = await self.wallet_state_manager.dl_store.get_latest_singleton(
            launcher_id
        )
        if singleton_record is not None:
            if (  # This is an unconfirmed singleton that we know about
                singleton_record.coin_id == new_singleton.name() and not singleton_record.confirmed
            ):
                timestamp = await self.wallet_state_manager.wallet_node.get_timestamp_for_height(height)
                await self.wallet_state_manager.dl_store.set_confirmed(singleton_record.coin_id, height, timestamp)
            else:
                self.log.info(f"Spend of launcher {launcher_id} has already been processed")
                return None
        else:
            timestamp = await self.wallet_state_manager.wallet_node.get_timestamp_for_height(height)
            await self.wallet_state_manager.dl_store.add_singleton_record(
                SingletonRecord(
                    coin_id=new_singleton.name(),
                    launcher_id=launcher_id,
                    root=root,
                    inner_puzzle_hash=inner_puzhash,
                    confirmed=True,
                    confirmed_at_height=height,
                    timestamp=timestamp,
                    lineage_proof=LineageProof(
                        launcher_id,
                        create_host_layer_puzzle(inner_puzhash, root).get_tree_hash(inner_puzhash),
                        amount,
                    ),
                    generation=uint32(0),
                ),
                in_transaction,
            )

        await self.wallet_state_manager.dl_store.add_launcher(launcher_spend.coin, in_transaction)
        await self.wallet_state_manager.add_interested_puzzle_hashes([launcher_id], [self.id()], in_transaction)
        await self.wallet_state_manager.add_interested_coin_ids([new_singleton.name()], in_transaction)
        await self.wallet_state_manager.coin_store.add_coin_record(
            WalletCoinRecord(
                new_singleton,
                height,
                uint32(0),
                False,
                False,
                WalletType(self.type()),
                self.id(),
            )
        )

    ################
    # TRANSACTIONS #
    ################

    async def generate_new_reporter(
        self,
        initial_root: bytes32,
        fee: uint64 = uint64(0),
    ) -> Tuple[TransactionRecord, TransactionRecord, bytes32]:
        """
        Creates the initial singleton, which includes spending an origin coin, the launcher, and creating a singleton
        """

        coins: Set[Coin] = await self.standard_wallet.select_coins(uint64(fee + 1))
        if coins is None:
            raise ValueError("Not enough coins to create new data layer singleton")

        launcher_parent: Coin = list(coins)[0]
        launcher_coin: Coin = Coin(launcher_parent.name(), SINGLETON_LAUNCHER.get_tree_hash(), uint64(1))

        inner_puzzle: Program = await self.standard_wallet.get_new_puzzle()
        full_puzzle: Program = create_host_fullpuz(inner_puzzle, initial_root, launcher_coin.name())

        genesis_launcher_solution: Program = Program.to(
            [full_puzzle.get_tree_hash(), 1, [initial_root, inner_puzzle.get_tree_hash()]]
        )
        announcement_message: bytes32 = genesis_launcher_solution.get_tree_hash()
        announcement = Announcement(launcher_coin.name(), announcement_message)
        create_launcher_tx_record: Optional[TransactionRecord] = await self.standard_wallet.generate_signed_transaction(
            amount=uint64(1),
            puzzle_hash=SINGLETON_LAUNCHER.get_tree_hash(),
            fee=fee,
            origin_id=launcher_parent.name(),
            coins=coins,
            primaries=None,
            ignore_max_send_amount=False,
            coin_announcements_to_consume={announcement},
        )
        assert create_launcher_tx_record is not None and create_launcher_tx_record.spend_bundle is not None

        launcher_cs: CoinSpend = CoinSpend(
            launcher_coin,
            SerializedProgram.from_program(SINGLETON_LAUNCHER),
            SerializedProgram.from_program(genesis_launcher_solution),
        )
        launcher_sb: SpendBundle = SpendBundle([launcher_cs], G2Element())
        full_spend: SpendBundle = SpendBundle.aggregate([create_launcher_tx_record.spend_bundle, launcher_sb])

        # Delete from standard transaction so we don't push duplicate spends
        std_record: TransactionRecord = dataclasses.replace(create_launcher_tx_record, spend_bundle=None)
        dl_record = TransactionRecord(
            confirmed_at_height=uint32(0),
            created_at_time=uint64(int(time.time())),
            to_puzzle_hash=bytes32([2] * 32),
            amount=uint64(1),
            fee_amount=fee,
            confirmed=False,
            sent=uint32(10),
            spend_bundle=full_spend,
            additions=full_spend.additions(),
            removals=full_spend.removals(),
            memos=list(compute_memos(full_spend).items()),
            wallet_id=uint32(0),  # This is being called before the wallet is created so we're using a temp ID of 0
            sent_to=[],
            trade_id=None,
            type=uint32(TransactionType.INCOMING_TX.value),
            name=full_spend.name(),
        )
        singleton_record = SingletonRecord(
            coin_id=Coin(launcher_coin.name(), full_puzzle.get_tree_hash(), uint64(1)).name(),
            launcher_id=launcher_coin.name(),
            root=initial_root,
            inner_puzzle_hash=inner_puzzle.get_tree_hash(),
            confirmed=False,
            confirmed_at_height=uint32(0),
            timestamp=uint64(0),
            lineage_proof=LineageProof(
                launcher_coin.name(),
                create_host_layer_puzzle(inner_puzzle, initial_root).get_tree_hash(),
                uint64(1),
            ),
            generation=uint32(0),
        )

        await self.wallet_state_manager.dl_store.add_singleton_record(singleton_record, False)
        await self.wallet_state_manager.add_interested_puzzle_hashes([singleton_record.launcher_id], [self.id()], False)

        return dl_record, std_record, launcher_coin.name()

    async def create_tandem_xch_tx(
        self,
        fee: uint64,
        announcement_to_assert: Announcement,
        coin_announcement: bool = True,
        in_transaction: bool = False,
    ) -> TransactionRecord:
        chia_tx = await self.standard_wallet.generate_signed_transaction(
            amount=uint64(0),
            puzzle_hash=await self.standard_wallet.get_new_puzzlehash(in_transaction=in_transaction),
            fee=fee,
            negative_change_allowed=False,
            coin_announcements_to_consume={announcement_to_assert} if coin_announcement else None,
            puzzle_announcements_to_consume=None if coin_announcement else {announcement_to_assert},
            in_transaction=in_transaction,
        )
        assert chia_tx.spend_bundle is not None
        return chia_tx

    async def create_update_state_spend(
        self,
        launcher_id: bytes32,
        root_hash: bytes32,
        fee: uint64 = uint64(0),
        in_transaction: bool = False,
    ) -> List[TransactionRecord]:
        singleton_record, parent_lineage = await self.get_spendable_singleton_info(launcher_id)

        inner_puzzle_derivation: Optional[
            DerivationRecord
        ] = await self.wallet_state_manager.puzzle_store.get_derivation_record_for_puzzle_hash(
            singleton_record.inner_puzzle_hash
        )
        if inner_puzzle_derivation is None:
            raise ValueError(f"DL Wallet does not have permission to update Singleton with launcher ID {launcher_id}")

        # Make the child's puzzles
        next_inner_puzzle: Program = await self.standard_wallet.get_new_puzzle(in_transaction=in_transaction)
        next_full_puz = create_host_fullpuz(next_inner_puzzle, root_hash, launcher_id)

        # Construct the current puzzles
        current_inner_puzzle: Program = self.standard_wallet.puzzle_for_pk(inner_puzzle_derivation.pubkey)
        current_full_puz = create_host_fullpuz(
            current_inner_puzzle,
            singleton_record.root,
            launcher_id,
        )

        # Make the solution to the current coin
        assert singleton_record.lineage_proof.parent_name is not None
        assert singleton_record.lineage_proof.amount is not None
        primaries: List[AmountWithPuzzlehash] = [
            {
                "puzzlehash": next_inner_puzzle.get_tree_hash(),
                "amount": singleton_record.lineage_proof.amount,
                "memos": [launcher_id, root_hash, next_inner_puzzle.get_tree_hash()],
            }
        ]
        inner_sol: Program = self.standard_wallet.make_solution(
            primaries=primaries,
            coin_announcements={b"$"} if fee > 0 else None,
        )
        magic_condition = Program.to([-24, ACS_MU, [[Program.to((root_hash, None)), ACS_MU_PH], None]])
        # TODO: This line is a hack, make_solution should allow us to pass extra conditions to it
        inner_sol = Program.to([[], (1, magic_condition.cons(inner_sol.at("rfr"))), []])
        db_layer_sol = Program.to([inner_sol])
        full_sol = Program.to(
            [
                parent_lineage.to_program(),
                singleton_record.lineage_proof.amount,
                db_layer_sol,
            ]
        )

        # Create the spend
        current_coin = Coin(
            singleton_record.lineage_proof.parent_name,
            current_full_puz.get_tree_hash(),
            singleton_record.lineage_proof.amount,
        )
        coin_spend = CoinSpend(
            current_coin,
            SerializedProgram.from_program(current_full_puz),
            SerializedProgram.from_program(full_sol),
        )
        await self.standard_wallet.hack_populate_secret_key_for_puzzle_hash(current_inner_puzzle.get_tree_hash())
        spend_bundle = await self.sign(coin_spend)

        dl_tx = TransactionRecord(
            confirmed_at_height=uint32(0),
            created_at_time=uint64(int(time.time())),
            to_puzzle_hash=next_inner_puzzle.get_tree_hash(),
            amount=uint64(singleton_record.lineage_proof.amount),
            fee_amount=fee,
            confirmed=False,
            sent=uint32(10),
            spend_bundle=spend_bundle,
            additions=spend_bundle.additions(),
            removals=spend_bundle.removals(),
            memos=list(compute_memos(spend_bundle).items()),
            wallet_id=self.id(),
            sent_to=[],
            trade_id=None,
            type=uint32(TransactionType.OUTGOING_TX.value),
            name=singleton_record.coin_id,
        )
        if fee > 0:
            chia_tx = await self.create_tandem_xch_tx(
                fee, Announcement(current_coin.name(), b"$"), coin_announcement=True, in_transaction=in_transaction
            )
            aggregate_bundle = SpendBundle.aggregate([dl_tx.spend_bundle, chia_tx.spend_bundle])
            dl_tx = dataclasses.replace(dl_tx, spend_bundle=aggregate_bundle)
            chia_tx = dataclasses.replace(chia_tx, spend_bundle=None)
            txs: List[TransactionRecord] = [dl_tx, chia_tx]
        else:
            txs = [dl_tx]
        new_singleton_record = SingletonRecord(
            coin_id=Coin(
                current_coin.name(), next_full_puz.get_tree_hash(), singleton_record.lineage_proof.amount
            ).name(),
            launcher_id=launcher_id,
            root=root_hash,
            inner_puzzle_hash=next_inner_puzzle.get_tree_hash(),
            confirmed=False,
            confirmed_at_height=uint32(0),
            timestamp=uint64(0),
            lineage_proof=LineageProof(
                singleton_record.coin_id,
                next_inner_puzzle.get_tree_hash(),
                singleton_record.lineage_proof.amount,
            ),
            generation=uint32(singleton_record.generation + 1),
        )
        await self.wallet_state_manager.dl_store.add_singleton_record(
            new_singleton_record,
            in_transaction=in_transaction,
        )
        return txs

    async def get_spendable_singleton_info(self, launcher_id: bytes32) -> Tuple[SingletonRecord, LineageProof]:
        # First, let's make sure this is a singleton that we track and that we can spend
        singleton_record: Optional[SingletonRecord] = await self.get_latest_singleton(launcher_id)
        if singleton_record is None:
            raise ValueError(f"Singleton with launcher ID {launcher_id} is not tracked by DL Wallet")

        # Next, the singleton should be confirmed or else we shouldn't be ready to spend it
        if not singleton_record.confirmed:
            raise ValueError(f"Singleton with launcher ID {launcher_id} is currently pending")

        # Next, let's verify we have all of the relevant coin information
        if singleton_record.lineage_proof.parent_name is None or singleton_record.lineage_proof.amount is None:
            raise ValueError(f"Singleton with launcher ID {launcher_id} has insufficient information to spend")

        # Finally, let's get the parent record for its lineage proof
        parent_singleton: Optional[SingletonRecord] = await self.wallet_state_manager.dl_store.get_singleton_record(
            singleton_record.lineage_proof.parent_name
        )
        parent_lineage: LineageProof
        if parent_singleton is None:
            if singleton_record.lineage_proof.parent_name != launcher_id:
                raise ValueError(f"Have not found the parent of singleton with launcher ID {launcher_id}")
            else:
                launcher_coin: Optional[Coin] = await self.wallet_state_manager.dl_store.get_launcher(launcher_id)
                if launcher_coin is None:
                    raise ValueError(f"DL Wallet does not have launcher info for id {launcher_id}")
                else:
                    parent_lineage = LineageProof(launcher_coin.parent_coin_info, None, launcher_coin.amount)
        else:
            parent_lineage = parent_singleton.lineage_proof

        return singleton_record, parent_lineage

    async def get_owned_singletons(self) -> List[SingletonRecord]:
        launcher_ids = await self.wallet_state_manager.dl_store.get_all_launchers()

        collected = []

        for launcher_id in launcher_ids:
            singleton_record = await self.wallet_state_manager.dl_store.get_latest_singleton(launcher_id=launcher_id)
            if singleton_record is None:
                # this is likely due to a race between getting the list and acquiring the extra data
                continue

            inner_puzzle_derivation: Optional[
                DerivationRecord
            ] = await self.wallet_state_manager.puzzle_store.get_derivation_record_for_puzzle_hash(
                singleton_record.inner_puzzle_hash
            )
            if inner_puzzle_derivation is not None:
                collected.append(singleton_record)

        return collected

    ###########
    # SYNCING #
    ###########

    async def singleton_removed(self, parent_spend: CoinSpend, height: uint32, in_transaction: bool = False) -> None:
        parent_name = parent_spend.coin.name()
        puzzle = parent_spend.puzzle_reveal
        solution = parent_spend.solution

        matched, _ = match_dl_singleton(puzzle.to_program())
        if matched:
            self.log.info(f"DL singleton removed: {parent_spend.coin}")
            singleton_record: Optional[SingletonRecord] = await self.wallet_state_manager.dl_store.get_singleton_record(
                parent_name
            )
            if singleton_record is None:
                self.log.warning(f"DL wallet received coin it does not have parent for. Expected parent {parent_name}.")
                return

            # First let's create the singleton's full puz to check if it's the same (report spend)
            current_full_puz_hash: bytes32 = create_host_fullpuz(
                singleton_record.inner_puzzle_hash,
                singleton_record.root,
                singleton_record.launcher_id,
            ).get_tree_hash(singleton_record.inner_puzzle_hash)

            # Information we need to create the singleton record
            full_puzzle_hash: bytes32
            amount: uint64
            root: bytes32
            inner_puzzle_hash: bytes32

            conditions = puzzle.run_with_cost(self.wallet_state_manager.constants.MAX_BLOCK_COST_CLVM, solution)[
                1
            ].as_python()
            found_singleton: bool = False
            for condition in conditions:
                if condition[0] == ConditionOpcode.CREATE_COIN and int.from_bytes(condition[2], "big") % 2 == 1:
                    full_puzzle_hash = bytes32(condition[1])
                    amount = uint64(int.from_bytes(condition[2], "big"))
                    try:
                        root = bytes32(condition[3][1])
                        inner_puzzle_hash = bytes32(condition[3][2])
                    except IndexError:
                        self.log.warning(
                            f"Parent {parent_name} with launcher {singleton_record.launcher_id} "
                            "did not hint its child properly"
                        )
                        return
                    found_singleton = True
                    break

            if not found_singleton:
                self.log.warning(f"Singleton with launcher ID {singleton_record.launcher_id} was melted")
                return

            new_singleton = Coin(parent_name, full_puzzle_hash, amount)
            timestamp = await self.wallet_state_manager.wallet_node.get_timestamp_for_height(height)
            await self.wallet_state_manager.dl_store.add_singleton_record(
                SingletonRecord(
                    coin_id=new_singleton.name(),
                    launcher_id=singleton_record.launcher_id,
                    root=root,
                    inner_puzzle_hash=inner_puzzle_hash,
                    confirmed=True,
                    confirmed_at_height=height,
                    timestamp=timestamp,
                    lineage_proof=LineageProof(
                        parent_name,
                        create_host_layer_puzzle(inner_puzzle_hash, root).get_tree_hash(inner_puzzle_hash),
                        amount,
                    ),
                    generation=uint32(singleton_record.generation + 1),
                ),
                True,
            )
            await self.wallet_state_manager.coin_store.add_coin_record(
                WalletCoinRecord(
                    new_singleton,
                    height,
                    uint32(0),
                    False,
                    False,
                    WalletType(self.type()),
                    self.id(),
                )
            )
            await self.wallet_state_manager.add_interested_coin_ids(
                [new_singleton.name()],
                in_transaction=in_transaction,
            )
            await self.potentially_handle_resubmit(singleton_record.launcher_id, in_transaction=in_transaction)

    async def potentially_handle_resubmit(self, launcher_id: bytes32, in_transaction: bool = False) -> None:
        """
        This method is meant to detect a fork in our expected pending singletons and the singletons that have actually
        been confirmed on chain.  If there is a fork and the root on chain never changed, we will attempt to rebase our
        singletons on to the new latest singleton.  If there is a fork and the root changed, we assume that everything
        has failed and delete any pending state.
        """
        unconfirmed_singletons = await self.wallet_state_manager.dl_store.get_unconfirmed_singletons(launcher_id)
        if len(unconfirmed_singletons) == 0:
            return
        unconfirmed_singletons = sorted(unconfirmed_singletons, key=attrgetter("generation"))
        full_branch: List[SingletonRecord] = await self.wallet_state_manager.dl_store.get_all_singletons_for_launcher(
            launcher_id,
            min_generation=unconfirmed_singletons[0].generation,
        )
        if len(unconfirmed_singletons) == len(full_branch) and set(unconfirmed_singletons) == set(full_branch):
            return

        # Now we have detected a fork so we should check whether the root changed at all
        self.log.info("Attempting automatic rebase")
        parent_name = unconfirmed_singletons[0].lineage_proof.parent_name
        assert parent_name is not None
        parent_singleton = await self.wallet_state_manager.dl_store.get_singleton_record(parent_name)
        if parent_singleton is None or any(parent_singleton.root != s.root for s in full_branch if s.confirmed):
            root_changed: bool = True
        else:
            root_changed = False

        # Regardless of whether the root changed or not, our old state is bad so let's eliminate it
        # First let's find all of our txs matching our unconfirmed singletons
        relevant_dl_txs: List[TransactionRecord] = []
        for singleton in unconfirmed_singletons:
            parent_name = singleton.lineage_proof.parent_name
            if parent_name is None:
                continue

            tx = await self.wallet_state_manager.tx_store.get_transaction_record(parent_name)
            if tx is not None:
                relevant_dl_txs.append(tx)
        # Let's check our standard wallet for fee transactions related to these dl txs
        all_spends: List[SpendBundle] = [tx.spend_bundle for tx in relevant_dl_txs if tx.spend_bundle is not None]
        all_removal_ids: Set[bytes32] = {removal.name() for sb in all_spends for removal in sb.removals()}
        unconfirmed_std_txs: List[
            TransactionRecord
        ] = await self.wallet_state_manager.tx_store.get_unconfirmed_for_wallet(self.standard_wallet.id())
        relevant_std_txs: List[TransactionRecord] = [
            tx for tx in unconfirmed_std_txs if any(c.name() in all_removal_ids for c in tx.removals)
        ]
        # Delete all of the relevant transactions
        for tx in [*relevant_dl_txs, *relevant_std_txs]:
            await self.wallet_state_manager.tx_store.delete_transaction_record(tx.name)
        # Delete all of the unconfirmed singleton records
        for singleton in unconfirmed_singletons:
            await self.wallet_state_manager.dl_store.delete_singleton_record(singleton.coin_id)

        if not root_changed:
            # The root never changed so let's attempt a rebase
            try:
                all_txs: List[TransactionRecord] = []
                for singleton in unconfirmed_singletons:
                    for tx in relevant_dl_txs:
                        if any(c.name() == singleton.coin_id for c in tx.additions):
                            if tx.spend_bundle is not None:
                                fee = uint64(tx.spend_bundle.fees())
                            else:
                                fee = uint64(0)

                            all_txs.extend(
                                await self.create_update_state_spend(
                                    launcher_id,
                                    singleton.root,
                                    fee,
                                    in_transaction=in_transaction,
                                )
                            )
                for tx in all_txs:
                    await self.wallet_state_manager.add_pending_transaction(tx, in_transaction=in_transaction)
            except Exception as e:
                self.log.warning(f"Something went wrong during attempted DL resubmit: {str(e)}")
                # Something went wrong so let's delete anything pending that was created
                for singleton in unconfirmed_singletons:
                    await self.wallet_state_manager.dl_store.delete_singleton_record(singleton.coin_id)

    async def stop_tracking_singleton(self, launcher_id: bytes32) -> None:
        await self.wallet_state_manager.dl_store.delete_singleton_records_by_launcher_id(launcher_id)
        await self.wallet_state_manager.dl_store.delete_launcher(launcher_id)

    ###########
    # UTILITY #
    ###########

    async def get_latest_singleton(
        self, launcher_id: bytes32, only_confirmed: bool = False
    ) -> Optional[SingletonRecord]:
        singleton: Optional[SingletonRecord] = await self.wallet_state_manager.dl_store.get_latest_singleton(
            launcher_id, only_confirmed
        )
        return singleton

    async def get_history(
        self,
        launcher_id: bytes32,
        min_generation: Optional[uint32] = None,
        max_generation: Optional[uint32] = None,
        num_results: Optional[uint32] = None,
    ) -> List[SingletonRecord]:
        history: List[SingletonRecord] = await self.wallet_state_manager.dl_store.get_all_singletons_for_launcher(
            launcher_id,
            min_generation,
            max_generation,
            num_results,
        )
        return history

    async def get_singleton_record(self, coin_id: bytes32) -> Optional[SingletonRecord]:
        singleton: Optional[SingletonRecord] = await self.wallet_state_manager.dl_store.get_singleton_record(coin_id)
        return singleton

    async def get_singletons_by_root(self, launcher_id: bytes32, root: bytes32) -> List[SingletonRecord]:
        singletons: List[SingletonRecord] = await self.wallet_state_manager.dl_store.get_singletons_by_root(
            launcher_id, root
        )
        return singletons

    ##########
    # WALLET #
    ##########

    def puzzle_for_pk(self, pubkey: bytes) -> Program:
        return self.standard_wallet.puzzle_for_pk(pubkey)

    async def get_new_puzzle(self) -> Program:
        return self.puzzle_for_pk(
            bytes((await self.wallet_state_manager.get_unused_derivation_record(self.wallet_info.id)).pubkey)
        )

    async def new_peak(self, peak: BlockRecord) -> None:
        pass

    async def get_confirmed_balance(self, record_list: Optional[Set[WalletCoinRecord]] = None) -> uint64:
        return uint64(0)

    async def get_unconfirmed_balance(self, record_list: Optional[Set[WalletCoinRecord]] = None) -> uint128:
        return uint128(0)

    async def get_spendable_balance(self, unspent_records: Optional[Set[WalletCoinRecord]] = None) -> uint128:
        return uint128(0)

    async def get_pending_change_balance(self) -> uint64:
        return uint64(0)

    async def get_max_send_amount(self, unspent_records: Optional[Set[WalletCoinRecord]] = None) -> uint128:
        return uint128(0)

    async def sign(self, coin_spend: CoinSpend) -> SpendBundle:
        return await sign_coin_spends(
            [coin_spend],
            self.standard_wallet.secret_key_store.secret_key_for_public_key,
            self.wallet_state_manager.constants.AGG_SIG_ME_ADDITIONAL_DATA,
            self.wallet_state_manager.constants.MAX_BLOCK_COST_CLVM,
        )
