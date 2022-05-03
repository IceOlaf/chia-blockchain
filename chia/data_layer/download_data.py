import aiohttp
import os
from pathlib import Path
from typing import List, Optional
from chia.data_layer.data_store import DataStore
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.data_layer.data_layer_types import NodeType, Status, SerializedNode
from chia.util.ints import uint16


def get_full_tree_filename(tree_id: bytes32, node_hash: bytes32, generation: int) -> str:
    return f"{tree_id}-{node_hash}-{generation}-v1.0.dat"


def get_delta_filename(tree_id: bytes32, node_hash: bytes32, generation: int) -> str:
    return f"{tree_id}-{node_hash}-delta-{generation}-v1.0.dat"


async def insert_into_data_store(
    data_store: DataStore,
    tree_id: bytes32,
    root_hash: Optional[bytes32],
    filename: str,
) -> None:
    with open(filename, "rb") as reader:
        while True:
            chunk = reader.read(4)
            if chunk is None or chunk == b"":
                break

            size = int.from_bytes(chunk, byteorder="big")
            serialize_nodes_bytes = reader.read(size)
            serialized_node = SerializedNode.from_bytes(serialize_nodes_bytes)

            if serialized_node.is_terminal:
                await data_store.insert_node(NodeType.TERMINAL, serialized_node.value1, serialized_node.value2)
            else:
                await data_store.insert_node(NodeType.INTERNAL, serialized_node.value1, serialized_node.value2)

    await data_store.insert_batch_root(tree_id, root_hash, Status.COMMITTED)


async def insert_from_delta_file(
    data_store: DataStore,
    tree_id: bytes32,
    existing_generation: int,
    root_hashes: List[bytes32],
    ip: str,
    port: uint16,
    client_foldername: Path,
) -> bool:
    for root_hash in root_hashes:
        existing_generation += 1
        filename = get_delta_filename(tree_id, root_hash, existing_generation)
        url = f"http://{ip}:{port}/{filename}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise RuntimeError("Didn't get 200 response status.")

                    target_filename = os.path.join(client_foldername, filename)
                    with open(target_filename, "wb") as writer:
                        text = await resp.read()
                        writer.write(text)
        except Exception:
            if await data_store.get_last_tree_root_by_hash(tree_id, root_hash) is not None:
                # If we don't have the delta file, but we have the tree in the past, create an empty delta file.
                # It's possible the wallet record to be created by a proof of inclusion, not a batch update,
                # hence the delta file might be missing.
                open(filename, "ab").close()
                pass
            raise

        await insert_into_data_store(
            data_store, tree_id, None if root_hash == bytes32([0] * 32) else root_hash, filename
        )

    return True
