# TODO: remove or formalize this
import aiosqlite as aiosqlite

from chia.data_layer.data_layer_types import node_type_to_class, Node
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.byte_types import hexstr_to_bytes


async def _debug_dump(db: aiosqlite.Connection, description: str = "") -> None:
    cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("-" * 50, description, flush=True)
    for [name] in await cursor.fetchall():
        cursor = await db.execute(f"SELECT * FROM {name}")
        print(f"\n -- {name} ------", flush=True)
        async for row in cursor:
            print(f"        {dict(row)}")


def hexstr_to_bytes32(hexstr: str) -> bytes32:
    return bytes32(hexstr_to_bytes(hexstr))


def row_to_node(row: aiosqlite.Row) -> Node:
    cls = node_type_to_class[row["type"]]
    return cls.from_row(row=row)
