import asyncio

import pytest

from src.util.MerkleSet import ReferenceMerkleSet, confirm_included_already_hashed
from tests.setup_nodes import test_constants, bt
from tests.wallet_tools import WalletTool


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


class TestMerkleSet:
    @pytest.mark.asyncio
    async def test_basics(self):
        wallet_tool = WalletTool()

        num_blocks = 10
        blocks = bt.get_consecutive_blocks(
            test_constants,
            num_blocks,
            [],
            10,
            reward_puzzlehash=wallet_tool.get_new_puzzlehash(),
        )

        merkle_set = ReferenceMerkleSet()
        for block in blocks:
            merkle_set.add_already_hashed(block.body.coinbase.name())

        for block in blocks:
            result, proof = merkle_set.is_included_already_hashed(block.body.coinbase.name())
            assert result is True
            result_fee, proof_fee = merkle_set.is_included_already_hashed(block.body.fees_coin.name())
            assert result_fee is False
            validate_proof = confirm_included_already_hashed(merkle_set.get_root(), block.body.coinbase.name(), proof)
            validate_proof_fee = confirm_included_already_hashed(merkle_set.get_root(), block.body.fees_coin.name(), proof_fee)
            assert validate_proof is True
            assert validate_proof_fee is False
