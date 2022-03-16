from dataclasses import dataclass
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Type, TypeVar

from blspy import AugSchemeMPL
import pytest

from chia.util.streamable import Streamable, streamable
from chia.types.blockchain_format.coin import Coin
from chia.wallet.db_wallet.db_wallet_puzzles import create_offer_fullpuz
from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_spend import CoinSpend
from chia.types.spend_bundle import SpendBundle
from chia.util.ints import uint8, uint32, uint64, uint128
from chia.wallet.transaction_record import TransactionRecord
from chia.wallet.util.compute_memos import compute_memos
from chia.wallet.util.transaction_type import TransactionType
from chia.wallet.util.wallet_types import WalletType
from chia.wallet.wallet import Wallet
from chia.wallet.wallet_coin_record import WalletCoinRecord
from chia.wallet.wallet_info import WalletInfo
from chia.wallet.wallet_state_manager import WalletStateManager


pytestmark = pytest.mark.data_layer


_T_DLOWallet = TypeVar("_T_DLOWallet", bound="DLOWallet")


@dataclass(frozen=True)
@streamable
class DLOInfo(Streamable):
    leaf_reveal: Optional[bytes]
    host_genesis_id: Optional[bytes32]
    claim_target: Optional[bytes32]
    recovery_target: Optional[bytes32]
    recovery_timelock: Optional[uint64]
    active_offer: Optional[Coin]


@dataclass
class DLOWallet:
    wallet_state_manager: WalletStateManager
    log: logging.Logger
    wallet_id: uint32
    wallet_info: WalletInfo
    dlo_info: DLOInfo
    standard_wallet: Wallet
    base_puzzle_program: Optional[bytes]
    base_inner_puzzle_hash: Optional[bytes32]
    cost_of_single_tx: Optional[int]

    @classmethod
    def type(cls) -> uint8:
        return uint8(WalletType.DATA_LAYER_OFFER)

    @classmethod
    async def create_new_dlo_wallet(
        cls: Type[_T_DLOWallet],
        wallet_state_manager: Any,
        wallet: Wallet,
    ) -> _T_DLOWallet:
        dlo_info = DLOInfo(None, None, None, None, None, None)
        info_as_string = bytes(dlo_info).hex()
        wallet_info = await wallet_state_manager.user_store.create_wallet(
            "DLO Wallet", WalletType.DATA_LAYER_OFFER.value, info_as_string
        )
        if wallet_info is None:
            # TODO: this should be an exception way down at the source, not here
            raise ValueError("Internal Error")

        self = cls(
            cost_of_single_tx=None,
            base_puzzle_program=None,
            base_inner_puzzle_hash=None,
            standard_wallet=wallet,
            log=logging.getLogger(__name__),
            wallet_state_manager=wallet_state_manager,
            dlo_info=dlo_info,
            wallet_info=wallet_info,
            wallet_id=wallet_info.id,
        )

        await self.wallet_state_manager.add_new_wallet(self, self.wallet_info.id)
        return self

    def puzzle_for_pk(self, pubkey: bytes) -> Program:
        if self.dlo_info.leaf_reveal is not None:
            return create_offer_fullpuz(
                self.dlo_info.leaf_reveal,
                self.dlo_info.host_genesis_id,  # type: ignore[arg-type]
                self.dlo_info.claim_target,  # type: ignore[arg-type]
                self.dlo_info.recovery_target,  # type: ignore[arg-type]
                self.dlo_info.recovery_timelock,  # type: ignore[arg-type]
            )
        return Program.to(pubkey)  # type: ignore[no-any-return]

    def id(self) -> uint32:
        return self.wallet_info.id

    async def generate_datalayer_offer_spend(
        self,
        amount: uint64,
        leaf_reveal: bytes,
        host_genesis_id: bytes32,
        claim_target: bytes32,
        recovery_target: bytes32,
        recovery_timelock: uint64,
    ) -> TransactionRecord:
        full_puzzle: Program = create_offer_fullpuz(
            leaf_reveal,
            host_genesis_id,
            claim_target,
            recovery_target,
            recovery_timelock,
        )
        tr: TransactionRecord = await self.standard_wallet.generate_signed_transaction(
            amount, full_puzzle.get_tree_hash()
        )
        await self.wallet_state_manager.interested_store.add_interested_puzzle_hash(
            full_puzzle.get_tree_hash(), self.wallet_id, True
        )

        active_coin = None
        spend_bundle = tr.spend_bundle
        if spend_bundle is not None:
            for coin in spend_bundle.additions():
                if coin.puzzle_hash == full_puzzle.get_tree_hash():
                    active_coin = coin
        if active_coin is None:
            raise ValueError("Unable to find created coin")

        await self.standard_wallet.push_transaction(tr)
        dlo_info = DLOInfo(
            leaf_reveal,
            host_genesis_id,
            claim_target,
            recovery_target,
            recovery_timelock,
            active_coin,
        )
        await self.save_info(dlo_info, True)
        return tr

    async def claim_dl_offer(
        self,
        offer_coin: Coin,
        offer_full_puzzle: Program,
        db_innerpuz_hash: bytes32,
        current_root: bytes32,
        inclusion_proof: Tuple[Optional[int], List[Optional[List[bytes32]]]],
        fee: uint64 = uint64(0),
    ) -> SpendBundle:
        solution = Program.to([1, offer_coin.amount, db_innerpuz_hash, current_root, inclusion_proof])
        sb = SpendBundle([CoinSpend(offer_coin, offer_full_puzzle, solution)], AugSchemeMPL.aggregate([]))
        # ret = uncurry_offer_puzzle(offer_full_puzzle)
        # singleton_struct, leaf_reveal, claim_target, recovery_target, recovery_timelock = ret
        # tr = TransactionRecord(
        #     confirmed_at_height=uint32(0),
        #     created_at_time=uint64(int(time.time())),
        #     to_puzzle_hash=claim_target,
        #     amount=uint64(offer_coin.amount),
        #     fee_amount=uint64(fee),
        #     confirmed=False,
        #     sent=uint32(0),
        #     spend_bundle=sb,
        #     additions=list(sb.additions()),
        #     removals=list(sb.removals()),
        #     wallet_id=self.id(),
        #     sent_to=[],
        #     trade_id=None,
        #     type=uint32(TransactionType.OUTGOING_TX.value),
        #     name=sb.name(),
        # )
        # self.standard_wallet.push_transaction(tr)
        return sb

    async def create_recover_dl_offer_spend(
        self,
        leaf_reveal: Optional[bytes] = None,
        host_genesis_id: Optional[bytes32] = None,
        claim_target: Optional[bytes32] = None,
        recovery_target: Optional[bytes32] = None,
        recovery_timelock: Optional[uint64] = None,
        fee: uint64 = uint64(0),
    ) -> TransactionRecord:
        coin = self.dlo_info.active_offer
        if coin is None:
            raise ValueError("Active offer coin unexpectedly None")

        solution = Program.to([0, coin.amount])

        if leaf_reveal is None:
            leaf_reveal = self.dlo_info.leaf_reveal
            host_genesis_id = self.dlo_info.host_genesis_id
            claim_target = self.dlo_info.claim_target
            recovery_target = self.dlo_info.recovery_target
            recovery_timelock = self.dlo_info.recovery_timelock
        full_puzzle: Program = create_offer_fullpuz(
            leaf_reveal, host_genesis_id, claim_target, recovery_target, recovery_timelock  # type: ignore[arg-type]
        )
        coin_spend = CoinSpend(coin, full_puzzle, solution)
        sb = SpendBundle([coin_spend], AugSchemeMPL.aggregate([]))
        # TODO: fix optionality issue with to_puzzle_hash
        tr = TransactionRecord(
            confirmed_at_height=uint32(0),
            created_at_time=uint64(int(time.time())),
            to_puzzle_hash=recovery_target,  # type: ignore[arg-type]
            amount=uint64(coin.amount),
            fee_amount=uint64(fee),
            confirmed=False,
            sent=uint32(0),
            spend_bundle=sb,
            additions=list(sb.additions()),
            removals=list(sb.removals()),
            memos=list(compute_memos(sb).items()),
            wallet_id=self.id(),
            sent_to=[],
            trade_id=None,
            type=uint32(TransactionType.OUTGOING_TX.value),
            name=sb.name(),
        )
        await self.standard_wallet.push_transaction(tr)
        return tr

    async def get_coin(self) -> Coin:
        try:
            coins = await self.select_coins(uint64(1))
        except ValueError:
            # TODO: not really right exactly the same since there are two cases of ValueError...
            coins = set()

        if len(coins) > 1:
            return coins.pop()

        if self.dlo_info.active_offer is None:
            # TODO: is this what we want here?
            raise ValueError("Unable to get a coin, no coins selected and no active offer.")

        return self.dlo_info.active_offer

    async def get_confirmed_balance(self, record_list: Optional[Set[WalletCoinRecord]] = None) -> uint64:
        if record_list is None:
            record_list = await self.wallet_state_manager.coin_store.get_unspent_coins_for_wallet(self.id())

        amount: uint64 = uint64(0)
        for record in record_list:
            amount = uint64(amount + record.coin.amount)

        self.log.info(f"Confirmed balance for dlo wallet is {amount}")
        return uint64(amount)

    async def get_unconfirmed_balance(self, record_list: Optional[Set[WalletCoinRecord]] = None) -> uint64:
        # TODO: should the uint128 be changed?
        return await self.wallet_state_manager.get_unconfirmed_balance(self.id(), record_list)  # type: ignore[return-value]  # noqa: E501

    async def get_spendable_balance(self, unspent_records: Optional[Set[WalletCoinRecord]] = None) -> uint64:
        spendable_am = await self.wallet_state_manager.get_confirmed_spendable_balance_for_wallet(
            self.wallet_info.id, unspent_records
        )
        # TODO: should the uint128 be changed?
        return spendable_am  # type: ignore[return-value]

    async def select_coins(self, amount: uint64, exclude: Optional[List[Coin]] = None) -> Set[Coin]:
        """Returns a set of coins that can be used for generating a new transaction."""
        if exclude is None:
            exclude = []

        spendable_amount = await self.get_spendable_balance()
        if amount > spendable_amount:
            error_msg = f"Can't select {amount}, from spendable {spendable_amount} for wallet id {self.id()}"
            self.log.warning(error_msg)
            raise ValueError(error_msg)

        self.log.info(f"About to select coins for amount {amount}")
        unspent: List[WalletCoinRecord] = list(
            await self.wallet_state_manager.get_spendable_coins_for_wallet(self.wallet_info.id)
        )
        sum_value = 0
        used_coins: Set[Coin] = set()

        # Use older coins first
        unspent.sort(key=lambda r: r.confirmed_block_height)

        # Try to use coins from the store, if there isn't enough of "unused"
        # coins use change coins that are not confirmed yet
        unconfirmed_removals: Dict[bytes32, Coin] = await self.wallet_state_manager.unconfirmed_removals_for_wallet(
            self.wallet_info.id
        )
        for coinrecord in unspent:
            if sum_value >= amount and len(used_coins) > 0:
                break
            if coinrecord.coin.name() in unconfirmed_removals:
                continue
            if coinrecord.coin in exclude:
                continue
            sum_value += coinrecord.coin.amount
            used_coins.add(coinrecord.coin)

        # This happens when we couldn't use one of the coins because it's already used
        # but unconfirmed, and we are waiting for the change. (unconfirmed_additions)
        if sum_value < amount:
            raise ValueError(
                "Can't make this transaction at the moment. Waiting for the change from the previous transaction."
            )

        self.log.info(f"Successfully selected coins: {used_coins}")
        return used_coins

    async def save_info(self, dlo_info: DLOInfo, in_transaction: bool) -> None:
        self.dlo_info = dlo_info
        current_info = self.wallet_info
        info_as_string = bytes(self.dlo_info).hex()
        wallet_info = WalletInfo(current_info.id, current_info.name, current_info.type, info_as_string)
        self.wallet_info = wallet_info
        await self.wallet_state_manager.user_store.update_wallet(wallet_info, in_transaction)
        await self.wallet_state_manager.update_wallet_puzzle_hashes(self.wallet_info.id)
        return
