import pytest
import pytest_asyncio

from blspy import G2Element
from typing import Dict, Tuple

from chia.clvm.spend_sim import SpendSim, SimClient
from chia.wallet.db_wallet.db_wallet_puzzles import (
    create_host_fullpuz,
    create_offer_fullpuz,
    SINGLETON_LAUNCHER,
)
from chia.wallet.lineage_proof import LineageProof
from chia.wallet.puzzles.singleton_top_layer import solution_for_singleton
from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.mempool_inclusion_status import MempoolInclusionStatus
from chia.types.spend_bundle import SpendBundle
from chia.types.coin_spend import CoinSpend
from chia.util.ints import uint64
from chia.wallet.util.merkle_tree import MerkleTree

from tests.clvm.benchmark_costs import cost_of_spend_bundle


ACS = Program.to(1)
ACS_2 = Program.to([3, "2", 1, []])  # (if "2" 1 ()) == 1
ACS_PH = ACS.get_tree_hash()
ACS_2_PH = ACS_2.get_tree_hash()
SINGLETON_LAUNCHER_HASH = SINGLETON_LAUNCHER.get_tree_hash()
OFFER_AMOUNT = uint64(13)

pytestmark = pytest.mark.data_layer


SetupArgs = Tuple[SpendSim, SimClient, Coin, LineageProof, Coin, Coin, Program, Program]


class TestDLLifecycle:
    cost: Dict[str, int] = {}

    def get_merkle_tree(self, string: str) -> MerkleTree:
        return MerkleTree([Program.to(string).get_tree_hash(), Program.to(string).get_tree_hash()])

    def get_merkle_root(self, string: str) -> bytes32:
        return self.get_merkle_tree(string).calculate_root()

    def hash_merkle_value(self, string: str) -> bytes32:
        # https://github.com/Chia-Network/clvm/pull/102
        # https://github.com/Chia-Network/clvm/pull/106
        return Program.to(string).get_tree_hash()  # type: ignore[no-any-return]

    def get_merkle_proof(self, string: str) -> Program:
        proof = self.get_merkle_tree(string).generate_proof(self.hash_merkle_value(string))
        # https://github.com/Chia-Network/clvm/pull/102
        # https://github.com/Chia-Network/clvm/pull/106
        return Program.to(proof)  # type: ignore[no-any-return]

    @pytest_asyncio.fixture(scope="function")
    async def setup_sim_and_singleton(self) -> SetupArgs:
        # https://github.com/Chia-Network/chia-blockchain/pull/11819
        sim = await SpendSim.create()  # type: ignore[no-untyped-call]
        sim_client = SimClient(sim)  # type: ignore[no-untyped-call]
        await sim.farm_block()
        await sim.farm_block(ACS_PH)
        fund_coin = (await sim_client.get_coin_records_by_puzzle_hash(ACS_PH))[0].coin
        launcher_coin = Coin(fund_coin.name(), SINGLETON_LAUNCHER_HASH, uint64(1))
        singleton_puzzle = create_host_fullpuz(ACS_PH, self.get_merkle_root("init"), launcher_coin.name())
        good_puzzle = create_offer_fullpuz(
            self.hash_merkle_value("init"),
            launcher_coin.name(),
            ACS_2_PH,
            ACS_PH,
            uint64(60),  # 60 seconds
        )
        bad_puzzle = create_offer_fullpuz(
            self.hash_merkle_value("nope"),
            launcher_coin.name(),
            ACS_2_PH,
            ACS_PH,
            uint64(60),  # 60 seconds
        )
        bundle = SpendBundle(
            [
                CoinSpend(
                    fund_coin,
                    ACS,
                    Program.to(
                        [
                            [51, SINGLETON_LAUNCHER_HASH, 1],
                            [51, good_puzzle.get_tree_hash(), OFFER_AMOUNT],
                            [51, bad_puzzle.get_tree_hash(), OFFER_AMOUNT],
                        ]
                    ),
                ),
                CoinSpend(
                    launcher_coin,
                    SINGLETON_LAUNCHER,
                    Program.to([singleton_puzzle.get_tree_hash(), launcher_coin.amount, []]),
                ),
            ],
            G2Element(),
        )
        result = (await sim_client.push_tx(bundle))[0]
        assert result == MempoolInclusionStatus.SUCCESS
        self.cost["launch singleton and create two coins"] = cost_of_spend_bundle(bundle)
        await sim.farm_block()
        singleton = (await sim_client.get_coin_records_by_puzzle_hashes([singleton_puzzle.get_tree_hash()]))[0].coin
        good_offer_coin = (await sim_client.get_coin_records_by_puzzle_hashes([good_puzzle.get_tree_hash()]))[0].coin
        bad_offer_coin = (await sim_client.get_coin_records_by_puzzle_hashes([bad_puzzle.get_tree_hash()]))[0].coin
        return (
            sim,
            sim_client,
            singleton,
            LineageProof(parent_name=launcher_coin.parent_coin_info, amount=launcher_coin.amount),
            good_offer_coin,
            bad_offer_coin,
            good_puzzle,
            bad_puzzle,
        )

    @pytest.mark.asyncio()
    async def test_update(self, setup_sim_and_singleton: SetupArgs) -> None:
        sim, sim_client, singleton, lineage_proof = setup_sim_and_singleton[0:4]

        try:
            bundle = SpendBundle(
                [
                    CoinSpend(
                        singleton,
                        create_host_fullpuz(ACS_PH, self.get_merkle_root("init"), singleton.parent_coin_info),
                        solution_for_singleton(
                            lineage_proof,
                            singleton.amount,
                            Program.to(
                                [[
                                    [51, ACS_PH, singleton.amount],
                                    [-24, ACS, Program.to((self.get_merkle_root("update"), None))]
                                ]]
                            ),
                        ),
                    )
                ],
                G2Element(),
            )
            result = (await sim_client.push_tx(bundle))[0]
            assert result == MempoolInclusionStatus.SUCCESS
            self.cost["update spend"] = cost_of_spend_bundle(bundle)
            await sim.farm_block()
            new_singleton = (await sim_client.get_coin_records_by_parent_ids([singleton.name()]))[0].coin
            assert (
                new_singleton.puzzle_hash
                == create_host_fullpuz(
                    ACS_PH, self.get_merkle_root("update"), singleton.parent_coin_info
                ).get_tree_hash()
            )
        finally:
            # https://github.com/Chia-Network/chia-blockchain/pull/11819
            await sim.close()  # type: ignore[no-untyped-call]

    def test_cost(self) -> None:
        import json
        import logging

        log = logging.getLogger(__name__)
        log.warning(json.dumps(self.cost))
