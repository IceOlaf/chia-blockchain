import asyncio
import itertools
from typing import Collection, List, Optional, Set

from chia.consensus.block_record import BlockRecord
from chia.consensus.block_rewards import calculate_pool_reward, calculate_base_farmer_reward
from chia.full_node.full_node_api import FullNodeAPI
from chia.protocols.full_node_protocol import RespondBlock
from chia.simulator.simulator_protocol import FarmNewBlockProtocol, ReorgProtocol
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.full_block import FullBlock
from chia.util.api_decorators import api_request
from chia.util.ints import uint8, uint32
from chia.wallet.transaction_record import TransactionRecord
from chia.wallet.wallet import Wallet


class FullNodeSimulator(FullNodeAPI):
    def __init__(self, full_node, block_tools) -> None:
        super().__init__(full_node)
        self.bt = block_tools
        self.full_node = full_node
        self.config = full_node.config
        self.time_per_block = None
        if "simulation" in self.config and self.config["simulation"] is True:
            self.use_current_time = True
        else:
            self.use_current_time = False

    async def get_all_full_blocks(self) -> List[FullBlock]:
        peak: Optional[BlockRecord] = self.full_node.blockchain.get_peak()
        if peak is None:
            return []
        blocks = []
        peak_block = await self.full_node.blockchain.get_full_block(peak.header_hash)
        if peak_block is None:
            return []
        blocks.append(peak_block)
        current = peak_block
        while True:
            prev = await self.full_node.blockchain.get_full_block(current.prev_header_hash)
            if prev is not None:
                current = prev
                blocks.append(prev)
            else:
                break

        blocks.reverse()
        return blocks

    @api_request
    async def farm_new_transaction_block(self, request: FarmNewBlockProtocol) -> FullBlock:
        async with self.full_node._blockchain_lock_high_priority:
            self.log.info("Farming new block!")
            current_blocks = await self.get_all_full_blocks()
            if len(current_blocks) == 0:
                genesis = self.bt.get_consecutive_blocks(uint8(1))[0]
                await self.full_node.blockchain.receive_block(genesis)

            peak = self.full_node.blockchain.get_peak()
            assert peak is not None
            curr: BlockRecord = peak
            while not curr.is_transaction_block:
                curr = self.full_node.blockchain.block_record(curr.prev_hash)
            mempool_bundle = await self.full_node.mempool_manager.create_bundle_from_mempool(curr.header_hash)
            if mempool_bundle is None:
                spend_bundle = None
            else:
                spend_bundle = mempool_bundle[0]

            current_blocks = await self.get_all_full_blocks()
            target = request.puzzle_hash
            more = self.bt.get_consecutive_blocks(
                1,
                time_per_block=self.time_per_block,
                transaction_data=spend_bundle,
                farmer_reward_puzzle_hash=target,
                pool_reward_puzzle_hash=target,
                block_list_input=current_blocks,
                guarantee_transaction_block=True,
                current_time=self.use_current_time,
                previous_generator=self.full_node.full_node_store.previous_generator,
            )
            rr = RespondBlock(more[-1])
        await self.full_node.respond_block(rr)
        return more[-1]

    @api_request
    async def farm_new_block(self, request: FarmNewBlockProtocol):
        async with self.full_node._blockchain_lock_high_priority:
            self.log.info("Farming new block!")
            current_blocks = await self.get_all_full_blocks()
            if len(current_blocks) == 0:
                genesis = self.bt.get_consecutive_blocks(uint8(1))[0]
                await self.full_node.blockchain.receive_block(genesis)

            peak = self.full_node.blockchain.get_peak()
            assert peak is not None
            curr: BlockRecord = peak
            while not curr.is_transaction_block:
                curr = self.full_node.blockchain.block_record(curr.prev_hash)
            mempool_bundle = await self.full_node.mempool_manager.create_bundle_from_mempool(curr.header_hash)
            if mempool_bundle is None:
                spend_bundle = None
            else:
                spend_bundle = mempool_bundle[0]
            current_blocks = await self.get_all_full_blocks()
            target = request.puzzle_hash
            more = self.bt.get_consecutive_blocks(
                1,
                transaction_data=spend_bundle,
                farmer_reward_puzzle_hash=target,
                pool_reward_puzzle_hash=target,
                block_list_input=current_blocks,
                current_time=self.use_current_time,
            )
            rr: RespondBlock = RespondBlock(more[-1])
        await self.full_node.respond_block(rr)

    @api_request
    async def reorg_from_index_to_new_index(self, request: ReorgProtocol):
        new_index = request.new_index
        old_index = request.old_index
        coinbase_ph = request.puzzle_hash

        current_blocks = await self.get_all_full_blocks()
        block_count = new_index - old_index

        more_blocks = self.bt.get_consecutive_blocks(
            block_count,
            farmer_reward_puzzle_hash=coinbase_ph,
            pool_reward_puzzle_hash=coinbase_ph,
            block_list_input=current_blocks[: old_index + 1],
            force_overflow=True,
            guarantee_transaction_block=True,
            seed=32 * b"1",
        )

        for block in more_blocks:
            await self.full_node.respond_block(RespondBlock(block))

    async def process_blocks(self, count: int, farm_to: bytes32 = bytes32([0] * 32)) -> int:
        """Process the requested number of blocks including farming to the passed puzzle
        hash. Note that the rewards for the last block will not have been processed.
        Consider `.farm_blocks()` or `.farm_rewards()` if the goal is to receive XCH at
        an address.

        Arguments:
            count: The number of blocks to process.
            farm_to: The puzzle hash to farm the block rewards to.

        Returns:
            The total number of reward mojos for the processed blocks.
        """
        rewards = 0

        for i in range(count):
            block: FullBlock = await self.farm_new_transaction_block(FarmNewBlockProtocol(farm_to))
            height = uint32(block.height)
            rewards += calculate_pool_reward(height) + calculate_base_farmer_reward(height)

            # TODO: is there a thing we can check to confirm the block has been processed?
            await asyncio.sleep(0)

        return rewards

    async def farm_blocks(self, count: int, wallet: Wallet) -> int:
        """Farm the requested number of blocks to the passed wallet. This will
        process additional blocks as needed to process the reward transactions
        and also wait for the rewards to be present in the wallet.

        Arguments:
            count: The number of blocks to farm.
            wallet: The wallet to farm the block rewards to.

        Returns:
            The total number of reward mojos farmed to the requested address.
        """
        if count == 0:
            return 0

        rewards = await self.process_blocks(count=count, farm_to=await wallet.get_new_puzzlehash())
        await self.process_blocks(count=1)

        peak_height = self.full_node.blockchain.get_peak_height()
        if peak_height is None:
            raise RuntimeError("Peak height still None after processing at least one block")

        coin_records = await self.full_node.coin_store.get_coins_added_at_height(height=peak_height)

        while True:
            # TODO: is there a better way to get all coins from a wallet?
            confirmed_balance = await wallet.get_confirmed_balance()
            wallet_coins = await wallet.select_coins(confirmed_balance)

            block_reward_coins = {record.coin for record in coin_records}

            if block_reward_coins.issubset(wallet_coins):
                break

            await asyncio.sleep(0.050)

        return rewards

    async def farm_rewards(self, amount: int, wallet: Wallet) -> int:
        """Farm at least the requested amount of mojos to the passed wallet. Extra
        mojos will be received based on the block rewards at the present block height.
        The rewards will be present in the wall before returning.

        Arguments:
            amount: The minimum number of mojos to farm.
            wallet: The wallet to farm the block rewards to.

        Returns:
            The total number of reward mojos farmed to the requested wallet.
        """
        rewards = 0

        if amount == 0:
            return rewards

        height_before = self.full_node.blockchain.get_peak_height()
        if height_before is None:
            height_before = uint32(0)

        for count in itertools.count(1):
            height = uint32(height_before + count)
            rewards += calculate_pool_reward(height) + calculate_base_farmer_reward(height)

            if rewards >= amount:
                await self.farm_blocks(count=count, wallet=wallet)
                return rewards

        raise Exception("internal error")

    async def wait_transaction_records_entered_mempool(self, records: Collection[TransactionRecord]) -> None:
        """Wait until the transaction records have entered the mempool.  Transaction
        records with no spend bundle are ignored.

        Arguments:
            records: The transaction records to wait for.
        """
        ids_to_check: Set[bytes32] = set()
        for record in records:
            if record.spend_bundle is None:
                raise ValueError(f"Transaction record has no spend bundle: {record!r}")

            ids_to_check.add(record.spend_bundle.name())

        while True:
            found = set()
            for spend_bundle_name in ids_to_check:
                tx = self.full_node.mempool_manager.get_spendbundle(spend_bundle_name)
                if tx is not None:
                    found.add(spend_bundle_name)
            ids_to_check = ids_to_check.difference(found)

            if len(ids_to_check) == 0:
                return

            await asyncio.sleep(0.050)

    async def process_transaction_records(self, records: Collection[TransactionRecord]) -> None:
        """Process the specified transaction records and wait until they have been
        included in a block.

        Arguments:
            records: The transaction records to process.
        """
        coin_names_to_wait_for: Set[bytes32] = set()
        for record in records:
            if record.spend_bundle is None:
                continue

            coin_names_to_wait_for.update(record.spend_bundle.additions())

        coin_store = self.full_node.coin_store

        await self.wait_transaction_records_entered_mempool(records=records)

        while True:
            await self.process_blocks(count=1)

            found: Set[Coin] = set()
            for coin_name in coin_names_to_wait_for:
                if coin_store.get_coin_record(coin_name) is not None:
                    found.add(coin_name)

            coin_names_to_wait_for = coin_names_to_wait_for.difference(found)

            if len(coin_names_to_wait_for) == 0:
                return
