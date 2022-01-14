import asyncio
from typing import AsyncIterator, Dict, List, Tuple, Any
import pytest

# flake8: noqa: F401
from chia.data_layer.data_layer import DataLayer
from chia.rpc.data_layer_rpc_api import DataLayerRpcApi
from chia.rpc.wallet_rpc_api import WalletRpcApi
from chia.server.server import ChiaServer
from chia.simulator.full_node_simulator import FullNodeSimulator
from chia.simulator.simulator_protocol import FarmNewBlockProtocol
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.peer_info import PeerInfo
from chia.util.byte_types import hexstr_to_bytes
from chia.util.config import load_config
from chia.util.ints import uint16
from chia.wallet.transaction_record import TransactionRecord
from chia.wallet.wallet_node import WalletNode
from tests.core.data_layer.util import ChiaRoot
from tests.setup_nodes import setup_simulators_and_wallets, self_hostname
from tests.time_out_assert import time_out_assert
from tests.wallet.rl_wallet.test_rl_rpc import is_transaction_confirmed

pytestmark = pytest.mark.data_layer
nodes = Tuple[List[FullNodeSimulator], List[Tuple[WalletNode, ChiaServer]]]


async def init_data_layer(
    full_node_api: Any, num_blocks: int, ph: bytes32, wallet_node: WalletNode, wallet_rpc_api: WalletRpcApi
) -> DataLayerRpcApi:
    assert wallet_node.wallet_state_manager
    data_layer = DataLayer(wallet_node.root_path, wallet_node)
    data_rpc_api = DataLayerRpcApi(data_layer)
    # res = await data_rpc_api.create_data_layer({"fee": 1})
    # await asyncio.sleep(1)
    # assert res["result"]
    # tx0: TransactionRecord = res["result"][0]
    # tx1: TransactionRecord = res["result"][1]
    # await asyncio.sleep(1)
    # for i in range(0, num_blocks):
    #     await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
    # await time_out_assert(15, is_transaction_confirmed, True, tx0.wallet_id, wallet_rpc_api, tx0.name)
    # await time_out_assert(15, is_transaction_confirmed, True, tx1.wallet_id, wallet_rpc_api, tx1.name)
    return data_rpc_api


@pytest.fixture(scope="function")
async def one_wallet_node() -> AsyncIterator[nodes]:
    async for _ in setup_simulators_and_wallets(1, 1, {}):
        yield _


@pytest.mark.asyncio
async def test_create_insert_get(chia_root: ChiaRoot, one_wallet_node: nodes) -> None:
    root = chia_root.path
    config = load_config(root, "config.yaml")
    config["data_layer"]["database_path"] = "data_layer_test.sqlite"
    num_blocks = 5
    full_nodes, wallets = one_wallet_node
    full_node_api = full_nodes[0]
    server_1 = full_node_api.full_node.server
    wallet_node, server_2 = wallets[0]
    assert wallet_node.wallet_state_manager is not None
    wallet = wallet_node.wallet_state_manager.main_wallet
    ph = await wallet.get_new_puzzlehash()
    await server_2.start_client(PeerInfo(self_hostname, uint16(server_1._port)), None)
    for i in range(0, num_blocks):
        await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
    wallet_rpc_api = WalletRpcApi(wallet_node)
    data_rpc_api = await init_data_layer(full_node_api, num_blocks, ph, wallet_node, wallet_rpc_api)
    key = b"a"
    value = b"\x00\x01"
    changelist: List[Dict[str, str]] = [{"action": "insert", "key": key.hex(), "value": value.hex()}]
    res = await data_rpc_api.create_data_store()
    await asyncio.sleep(1)
    assert res is not None
    store_id = bytes32(hexstr_to_bytes(res["id"]))
    res = await data_rpc_api.batch_update({"id": store_id.hex(), "changelist": changelist})
    update_tx_rec0 = res["tx_id"]
    await asyncio.sleep(1)
    for i in range(0, num_blocks):
        await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
    await time_out_assert(
        15, is_transaction_confirmed, True, update_tx_rec0.wallet_id, wallet_rpc_api, update_tx_rec0.name
    )
    res = await data_rpc_api.get_value({"id": store_id.hex(), "key": key.hex()})
    assert hexstr_to_bytes(res["data"]) == value
    changelist = [{"action": "delete", "key": key.hex()}]
    res = await data_rpc_api.batch_update({"id": store_id.hex(), "changelist": changelist})
    update_tx_rec1 = res["tx_id"]
    await asyncio.sleep(1)
    for i in range(0, num_blocks):
        await asyncio.sleep(1)
        await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
    await time_out_assert(
        15, is_transaction_confirmed, True, update_tx_rec1.wallet_id, wallet_rpc_api, update_tx_rec1.name
    )
    with pytest.raises(Exception):
        val = await data_rpc_api.get_value({"id": store_id.hex(), "key": key.hex()})


@pytest.mark.asyncio
async def test_create_double_insert(chia_root: ChiaRoot, one_wallet_node: nodes) -> None:
    root = chia_root.path
    config = load_config(root, "config.yaml")
    config["data_layer"]["database_path"] = "data_layer_test.sqlite"
    num_blocks = 5
    full_nodes, wallets = one_wallet_node
    full_node_api = full_nodes[0]
    server_1 = full_node_api.full_node.server
    wallet_node, server_2 = wallets[0]
    assert wallet_node.wallet_state_manager is not None
    wallet = wallet_node.wallet_state_manager.main_wallet
    ph = await wallet.get_new_puzzlehash()
    await server_2.start_client(PeerInfo(self_hostname, uint16(server_1._port)), None)
    for i in range(0, num_blocks):
        await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
    print(f"confirmed balance is {await wallet.get_confirmed_balance()}")
    print(f"unconfirmed balance is {await wallet.get_unconfirmed_balance()}")
    wallet_rpc_api = WalletRpcApi(wallet_node)
    data_rpc_api = await init_data_layer(full_node_api, num_blocks, ph, wallet_node, wallet_rpc_api)
    key1 = b"a"
    value1 = b"\x01\x02"
    key2 = b"b"
    value2 = b"\x01\x23"
    changelist: List[Dict[str, str]] = [{"action": "insert", "key": key1.hex(), "value": value1.hex()}]
    res = await data_rpc_api.create_data_store()
    store_id = bytes32(hexstr_to_bytes(res["id"]))
    res = await data_rpc_api.batch_update({"id": store_id.hex(), "changelist": changelist})
    update_tx_rec0 = res["tx_id"]
    await asyncio.sleep(1)
    for i in range(0, num_blocks):
        await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
    await time_out_assert(
        15, is_transaction_confirmed, True, update_tx_rec0.wallet_id, wallet_rpc_api, update_tx_rec0.name
    )

    res = await data_rpc_api.get_value({"id": store_id.hex(), "key": key1.hex()})
    assert hexstr_to_bytes(res["data"]) == value1

    changelist = [{"action": "insert", "key": key2.hex(), "value": value2.hex()}]
    res = await data_rpc_api.batch_update({"id": store_id.hex(), "changelist": changelist})
    update_tx_rec1 = res["tx_id"]
    await asyncio.sleep(1)
    for i in range(0, num_blocks):
        await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
    await time_out_assert(
        15, is_transaction_confirmed, True, update_tx_rec0.wallet_id, wallet_rpc_api, update_tx_rec1.name
    )
    res = await data_rpc_api.get_value({"id": store_id.hex(), "key": key2.hex()})
    assert hexstr_to_bytes(res["data"]) == value2

    changelist = [{"action": "delete", "key": key1.hex()}]
    await data_rpc_api.batch_update({"id": store_id.hex(), "changelist": changelist})
    with pytest.raises(Exception):
        val = await data_rpc_api.get_value({"id": store_id.hex(), "key": key1.hex()})


@pytest.mark.asyncio
async def test_get_keys_values(chia_root: ChiaRoot, one_wallet_node: nodes) -> None:
    root = chia_root.path
    config = load_config(root, "config.yaml")
    config["data_layer"]["database_path"] = "data_layer_test.sqlite"
    num_blocks = 5
    full_nodes, wallets = one_wallet_node
    full_node_api = full_nodes[0]
    server_1 = full_node_api.full_node.server
    wallet_node, server_2 = wallets[0]
    assert wallet_node.wallet_state_manager is not None
    wallet = wallet_node.wallet_state_manager.main_wallet
    ph = await wallet.get_new_puzzlehash()
    await server_2.start_client(PeerInfo(self_hostname, uint16(server_1._port)), None)
    for i in range(0, num_blocks):
        await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
    print(f"confirmed balance is {await wallet.get_confirmed_balance()}")
    print(f"unconfirmed balance is {await wallet.get_unconfirmed_balance()}")
    wallet_rpc_api = WalletRpcApi(wallet_node)
    data_rpc_api = await init_data_layer(full_node_api, num_blocks, ph, wallet_node, wallet_rpc_api)
    key1 = b"a"
    value1 = b"\x01\x02"
    changelist: List[Dict[str, str]] = [{"action": "insert", "key": key1.hex(), "value": value1.hex()}]
    key2 = b"b"
    value2 = b"\x03\x02"
    changelist.append({"action": "insert", "key": key2.hex(), "value": value2.hex()})
    key3 = b"c"
    value3 = b"\x04\x05"
    changelist.append({"action": "insert", "key": key3.hex(), "value": value3.hex()})
    key4 = b"d"
    value4 = b"\x06\x03"
    changelist.append({"action": "insert", "key": key4.hex(), "value": value4.hex()})
    key5 = b"e"
    value5 = b"\x07\x01"
    changelist.append({"action": "insert", "key": key5.hex(), "value": value5.hex()})
    res = await data_rpc_api.create_data_store()
    tree_id = bytes32(hexstr_to_bytes(res["id"]))
    res = await data_rpc_api.batch_update({"id": tree_id.hex(), "changelist": changelist})
    update_tx_rec0 = res["tx_id"]
    await asyncio.sleep(1)
    for i in range(0, num_blocks):
        await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
    await time_out_assert(
        15, is_transaction_confirmed, True, update_tx_rec0.wallet_id, wallet_rpc_api, update_tx_rec0.name
    )
    val = await data_rpc_api.get_keys_values({"id": tree_id.hex()})
    dic = {}
    for item in val["data"]:
        dic[item.key] = item.value
    assert dic[key1] == value1
    assert dic[key2] == value2
    assert dic[key3] == value3
    assert dic[key4] == value4
    assert dic[key5] == value5
    # todo check values match


@pytest.mark.asyncio
async def test_get_ancestors(chia_root: ChiaRoot, one_wallet_node: nodes) -> None:
    root = chia_root.path
    config = load_config(root, "config.yaml")
    config["data_layer"]["database_path"] = "data_layer_test.sqlite"
    num_blocks = 5
    full_nodes, wallets = one_wallet_node
    full_node_api = full_nodes[0]
    server_1 = full_node_api.full_node.server
    wallet_node, server_2 = wallets[0]
    assert wallet_node.wallet_state_manager
    wallet = wallet_node.wallet_state_manager.main_wallet
    ph = await wallet.get_new_puzzlehash()
    await server_2.start_client(PeerInfo(self_hostname, uint16(server_1._port)), None)
    for i in range(0, num_blocks):
        await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
    print(f"confirmed balance is {await wallet.get_confirmed_balance()}")
    print(f"unconfirmed balance is {await wallet.get_unconfirmed_balance()}")
    wallet_rpc_api = WalletRpcApi(wallet_node)
    data_rpc_api = await init_data_layer(full_node_api, num_blocks, ph, wallet_node, wallet_rpc_api)
    key1 = b"a"
    value1 = b"\x01\x02"
    changelist: List[Dict[str, str]] = [{"action": "insert", "key": key1.hex(), "value": value1.hex()}]
    key2 = b"b"
    value2 = b"\x03\x02"
    changelist.append({"action": "insert", "key": key2.hex(), "value": value2.hex()})
    key3 = b"c"
    value3 = b"\x04\x05"
    changelist.append({"action": "insert", "key": key3.hex(), "value": value3.hex()})
    key4 = b"d"
    value4 = b"\x06\x03"
    changelist.append({"action": "insert", "key": key4.hex(), "value": value4.hex()})
    key5 = b"e"
    value5 = b"\x07\x01"
    changelist.append({"action": "insert", "key": key5.hex(), "value": value5.hex()})
    res = await data_rpc_api.create_data_store()
    tree_id = bytes32(hexstr_to_bytes(res["id"]))
    res = await data_rpc_api.batch_update({"id": tree_id.hex(), "changelist": changelist})
    update_tx_rec0 = res["tx_id"]
    await asyncio.sleep(1)
    for i in range(0, num_blocks):
        await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
    await time_out_assert(
        15, is_transaction_confirmed, True, update_tx_rec0.wallet_id, wallet_rpc_api, update_tx_rec0.name
    )
    val = await data_rpc_api.get_keys_values({"id": tree_id.hex()})
    assert val["data"]
    val = await data_rpc_api.get_ancestors({"id": tree_id.hex(), "hash": val["data"][4].hash.hex()})
    print(val)
    # todo assert values


@pytest.mark.asyncio
async def test_get_roots(chia_root: ChiaRoot, one_wallet_node: nodes) -> None:
    root = chia_root.path
    config = load_config(root, "config.yaml")
    config["data_layer"]["database_path"] = "data_layer_test.sqlite"
    num_blocks = 5
    full_nodes, wallets = one_wallet_node
    full_node_api = full_nodes[0]
    server_1 = full_node_api.full_node.server
    wallet_node, server_2 = wallets[0]
    assert wallet_node.wallet_state_manager
    wallet = wallet_node.wallet_state_manager.main_wallet
    ph = await wallet.get_new_puzzlehash()
    await server_2.start_client(PeerInfo(self_hostname, uint16(server_1._port)), None)
    for i in range(0, num_blocks):
        await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
    print(f"confirmed balance is {await wallet.get_confirmed_balance()}")
    print(f"unconfirmed balance is {await wallet.get_unconfirmed_balance()}")
    wallet_rpc_api = WalletRpcApi(wallet_node)
    data_rpc_api = await init_data_layer(full_node_api, num_blocks, ph, wallet_node, wallet_rpc_api)
    res = await data_rpc_api.create_data_store()
    tree_id_1 = bytes32(hexstr_to_bytes(res["id"]))
    res = await data_rpc_api.create_data_store()
    tree_id_2 = bytes32(hexstr_to_bytes(res["id"]))
    key1 = b"a"
    value1 = b"\x01\x02"
    changelist: List[Dict[str, str]] = [{"action": "insert", "key": key1.hex(), "value": value1.hex()}]
    key2 = b"b"
    value2 = b"\x03\x02"
    changelist.append({"action": "insert", "key": key2.hex(), "value": value2.hex()})
    key3 = b"c"
    value3 = b"\x04\x05"
    changelist.append({"action": "insert", "key": key3.hex(), "value": value3.hex()})
    res = await data_rpc_api.batch_update({"id": tree_id_1.hex(), "changelist": changelist})
    update_tx_rec0: TransactionRecord = res["tx_id"]
    roots = await data_rpc_api.get_roots({"ids": [tree_id_1.hex(), tree_id_2.hex()]})
    print(f"roots {roots}")
    key4 = b"d"
    value4 = b"\x06\x03"
    changelist.append({"action": "insert", "key": key4.hex(), "value": value4.hex()})
    key5 = b"e"
    value5 = b"\x07\x01"
    changelist.append({"action": "insert", "key": key5.hex(), "value": value5.hex()})
    res = await data_rpc_api.batch_update({"id": tree_id_2.hex(), "changelist": changelist})
    update_tx_rec1: TransactionRecord = res["tx_id"]
    roots = await data_rpc_api.get_roots({"ids": [tree_id_1.hex(), tree_id_2.hex()]})
    print(f"roots {roots}")
    await asyncio.sleep(1)
    for i in range(0, num_blocks):
        await full_node_api.farm_new_transaction_block(FarmNewBlockProtocol(ph))
    await time_out_assert(
        15, is_transaction_confirmed, True, update_tx_rec1.wallet_id, wallet_rpc_api, update_tx_rec1.name
    )
