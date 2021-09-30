import json
from typing import Optional

import aiohttp

from chia.rpc.data_layer_rpc_client import DataLayerRpcClient
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.byte_types import hexstr_to_bytes
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ints import uint16


# TODO: there seems to be a large amount of repetition in these to dedupe


async def create_table(rpc_port: Optional[int], table_string: str, table_name: str) -> None:
    # TODO: nice cli error handling

    table_bytes = bytes32(hexstr_to_bytes(table_string))

    try:
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        self_hostname = config["self_hostname"]
        if rpc_port is None:
            rpc_port = config["data_layer"]["rpc_port"]
        # TODO: context manager for this and closing etc?
        client = await DataLayerRpcClient.create(self_hostname, uint16(rpc_port), DEFAULT_ROOT_PATH, config)
        row = await client.create_table(table=table_bytes, name=table_name)
    except aiohttp.ClientConnectorError:
        print(f"Connection error. Check if data is running at {rpc_port}")
        return None
    except Exception as e:
        print(f"Exception from 'data': {e}")
        return None

    client.close()
    await client.await_closed()
    return row


async def get_row(rpc_port: Optional[int], table_string: str, row_hash_string: str) -> None:
    # TODO: nice cli error handling

    row_hash_bytes = bytes32(hexstr_to_bytes(row_hash_string))
    table_bytes = bytes32(hexstr_to_bytes(table_string))

    try:
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        self_hostname = config["self_hostname"]
        if rpc_port is None:
            rpc_port = config["data_layer"]["rpc_port"]
        # TODO: context manager for this and closing etc?
        client = await DataLayerRpcClient.create(self_hostname, uint16(rpc_port), DEFAULT_ROOT_PATH, config)
        row = await client.get_row(table=table_bytes, row_hash=row_hash_bytes)
        print(json.dumps(row, indent=4))
    except aiohttp.ClientConnectorError:
        print(f"Connection error. Check if data is running at {rpc_port}")
        return None
    except Exception as e:
        print(f"Exception from 'data': {e}")
        return None

    client.close()
    await client.await_closed()
    return row


async def insert_row(rpc_port: Optional[int], table_string: str, row_data_string: str) -> None:
    # TODO: nice cli error handling

    row_data_bytes = hexstr_to_bytes(row_data_string)
    table_bytes = bytes32(hexstr_to_bytes(table_string))

    try:
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        self_hostname = config["self_hostname"]
        if rpc_port is None:
            rpc_port = config["data_layer"]["rpc_port"]
        # TODO: context manager for this and closing etc?
        client = await DataLayerRpcClient.create(self_hostname, uint16(rpc_port), DEFAULT_ROOT_PATH, config)
        row = await client.insert_row(table=table_bytes, row_data=row_data_bytes)
        print(json.dumps(row, indent=4))
    except aiohttp.ClientConnectorError:
        print(f"Connection error. Check if data is running at {rpc_port}")
        return None
    except Exception as e:
        print(f"Exception from 'data': {e}")
        return None

    client.close()
    await client.await_closed()
    return row
