import asyncio
import pytest
from chia.simulator.simulator_protocol import FarmNewBlockProtocol
from chia.types.peer_info import PeerInfo
from chia.util.ints import uint16, uint32, uint64
from tests.setup_nodes import setup_simulators_and_wallets
from chia.wallet.did_wallet.did_wallet import DIDWallet
from chia.wallet.nft_wallet.nft_wallet import NFTWallet
# from chia.types.blockchain_format.program import Program
# from blspy import AugSchemeMPL
# from chia.types.spend_bundle import SpendBundle
from chia.consensus.block_rewards import calculate_pool_reward, calculate_base_farmer_reward
from tests.time_out_assert import time_out_assert, time_out_assert_not_none

# pytestmark = pytest.mark.skip("TODO: Fix tests")


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


class TestNFTWallet:
    @pytest.fixture(scope="function")
    async def wallet_node(self):
        async for _ in setup_simulators_and_wallets(1, 1, {}):
            yield _

    @pytest.fixture(scope="function")
    async def two_wallet_nodes(self):
        async for _ in setup_simulators_and_wallets(1, 2, {}):
            yield _

    @pytest.fixture(scope="function")
    async def three_wallet_nodes(self):
        async for _ in setup_simulators_and_wallets(1, 3, {}):
            yield _

    @pytest.fixture(scope="function")
    async def two_wallet_nodes_five_freeze(self):
        async for _ in setup_simulators_and_wallets(1, 2, {}):
            yield _

    @pytest.fixture(scope="function")
    async def three_sim_two_wallets(self):
        async for _ in setup_simulators_and_wallets(3, 2, {}):
            yield _

    @pytest.mark.parametrize(
        "trusted",
        [True],
    )
    @pytest.mark.asyncio
    async def test_nft_wallet_creation(self, three_wallet_nodes, trusted):
        num_blocks = 5
        full_nodes, wallets = three_wallet_nodes
        full_node_api = full_nodes[0]
        full_node_server = full_node_api.server
        wallet_node_0, server_0 = wallets[0]
        wallet_node_1, server_1 = wallets[1]
        wallet_node_2, server_2 = wallets[2]
        wallet_0 = wallet_node_0.wallet_state_manager.main_wallet
        wallet_1 = wallet_node_1.wallet_state_manager.main_wallet
        wallet_2 = wallet_node_2.wallet_state_manager.main_wallet

        ph = await wallet_0.get_new_puzzlehash()
        ph1 = await wallet_1.get_new_puzzlehash()
        ph2 = await wallet_2.get_new_puzzlehash()

        if trusted:
            wallet_node_0.config["trusted_peers"] = {
                full_node_api.full_node.server.node_id.hex(): full_node_api.full_node.server.node_id.hex()
            }
            wallet_node_1.config["trusted_peers"] = {
                full_node_api.full_node.server.node_id.hex(): full_node_api.full_node.server.node_id.hex()
            }
            wallet_node_2.config["trusted_peers"] = {
                full_node_api.full_node.server.node_id.hex(): full_node_api.full_node.server.node_id.hex()
            }
        else:
            wallet_node_0.config["trusted_peers"] = {}
            wallet_node_1.config["trusted_peers"] = {}
            wallet_node_2.config["trusted_peers"] = {}

        await server_0.start_client(PeerInfo("localhost", uint16(full_node_server._port)), None)
        await server_1.start_client(PeerInfo("localhost", uint16(full_node_server._port)), None)
        await server_2.start_client(PeerInfo("localhost", uint16(full_node_server._port)), None)

        for i in range(1, num_blocks):
            await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))

        funds = sum(
            [
                calculate_pool_reward(uint32(i)) + calculate_base_farmer_reward(uint32(i))
                for i in range(1, num_blocks - 1)
            ]
        )

        await time_out_assert(10, wallet_0.get_unconfirmed_balance, funds)
        await time_out_assert(10, wallet_0.get_confirmed_balance, funds)
        for i in range(1, num_blocks):
            await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph1))
        for i in range(1, num_blocks):
            await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph2))

        # Wallet1 sets up DIDWallet1 without any backup set
        async with wallet_node_0.wallet_state_manager.lock:
            did_wallet_0: DIDWallet = await DIDWallet.create_new_did_wallet(
                wallet_node_0.wallet_state_manager, wallet_0, uint64(101)
            )

        spend_bundle_list = await wallet_node_0.wallet_state_manager.tx_store.get_unconfirmed_for_wallet(wallet_0.id())

        spend_bundle = spend_bundle_list[0].spend_bundle
        await time_out_assert_not_none(5, full_node_api.full_node.mempool_manager.get_spendbundle, spend_bundle.name())

        for i in range(1, num_blocks):
            await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))

        await time_out_assert(15, did_wallet_0.get_confirmed_balance, 101)
        await time_out_assert(15, did_wallet_0.get_unconfirmed_balance, 101)
        await time_out_assert(15, did_wallet_0.get_pending_change_balance, 0)

        nft_wallet_0 = await NFTWallet.create_new_nft_wallet(
            wallet_node_0.wallet_state_manager, wallet_0, did_wallet_0.id()
        )
        tr = await nft_wallet_0.generate_new_nft("https://www.chia.net/img/branding/chia-logo.svg", 20, ph)

        await time_out_assert_not_none(
            5, full_node_api.full_node.mempool_manager.get_spendbundle, tr.spend_bundle.name()
        )

        for i in range(1, num_blocks):
            await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph1))

        await asyncio.sleep(3)
        coins = nft_wallet_0.nft_wallet_info.my_nft_coins
        assert len(coins) == 1

        # Wallet2 sets up DIDWallet2 without any backup set
        async with wallet_node_1.wallet_state_manager.lock:
            did_wallet_1: DIDWallet = await DIDWallet.create_new_did_wallet(
                wallet_node_1.wallet_state_manager, wallet_1, uint64(201)
            )

        spend_bundle_list = await wallet_node_1.wallet_state_manager.tx_store.get_unconfirmed_for_wallet(wallet_1.id())

        spend_bundle = spend_bundle_list[0].spend_bundle
        await time_out_assert_not_none(5, full_node_api.full_node.mempool_manager.get_spendbundle, spend_bundle.name())

        for i in range(1, num_blocks):
            await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph1))

        await time_out_assert(15, did_wallet_1.get_confirmed_balance, 201)
        await time_out_assert(15, did_wallet_1.get_unconfirmed_balance, 201)
        nft_wallet_1 = await NFTWallet.create_new_nft_wallet(
            wallet_node_1.wallet_state_manager, wallet_1, did_wallet_1.id()
        )
        # nft_coin_info: NFTCoinInfo,
        # new_did,
        # new_did_parent,
        # new_did_inner_hash,
        # new_did_amount,
        # trade_price,
        did_coin_threeple = await did_wallet_1.get_info_for_recovery()
        trade_price = 10

        sb = await nft_wallet_0.transfer_nft(
            coins[0],
            nft_wallet_1.nft_wallet_info.my_did,
            did_coin_threeple[0],
            did_coin_threeple[1],
            did_coin_threeple[2],
            trade_price
        )
        assert sb is not None

        full_sb = await nft_wallet_1.receive_nft(sb)
        await asyncio.sleep(3)

        for i in range(1, num_blocks):
            await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph1))
        await asyncio.sleep(3)

        coins = nft_wallet_0.nft_wallet_info.my_nft_coins
        assert len(coins) == 0
        coins = nft_wallet_1.nft_wallet_info.my_nft_coins
        assert len(coins) == 1

        await asyncio.sleep(3)
        # Send it back to original owner
        did_coin_threeple = await did_wallet_0.get_info_for_recovery()
        trade_price = 10

        await asyncio.sleep(3)

        nsb = await nft_wallet_1.transfer_nft(
            coins[0],
            nft_wallet_0.nft_wallet_info.my_did,
            did_coin_threeple[0],
            did_coin_threeple[1],
            did_coin_threeple[2],
            trade_price
        )
        assert sb is not None

        full_sb = await nft_wallet_0.receive_nft(nsb)
        await asyncio.sleep(3)

        for i in range(1, num_blocks):
            await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph1))

        await asyncio.sleep(3)
        coins = nft_wallet_0.nft_wallet_info.my_nft_coins
        assert len(coins) == 1

        coins = nft_wallet_1.nft_wallet_info.my_nft_coins
        assert len(coins) == 0
