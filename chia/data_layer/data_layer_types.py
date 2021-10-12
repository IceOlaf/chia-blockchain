from dataclasses import dataclass, field
from enum import IntEnum
from typing import Tuple, Optional, Union, Dict, Type

import aiosqlite as aiosqlite

from chia.data_layer.data_layer_util import hexstr_to_bytes32
from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32

from clvm.CLVMObject import CLVMObject


class NodeType(IntEnum):
    # EMPTY = 0
    INTERNAL = 1
    TERMINAL = 2


class Side(IntEnum):
    LEFT = 0
    RIGHT = 1


class OperationType(IntEnum):
    INSERT = 0
    DELETE = 1


class CommitState(IntEnum):
    OPEN = 0
    FINALIZED = 1
    ROLLED_BACK = 2


Node = Union["TerminalNode", "InternalNode"]


@dataclass(frozen=True)
class TerminalNode:
    hash: bytes32
    # generation: int
    key: Program
    value: Program

    atom: None = field(init=False, default=None)

    @property
    def pair(self) -> Tuple[Program, Program]:
        return Program.to(CLVMObject(v=self.key.as_bin())), Program.to(CLVMObject(self.value.as_bin()))

    @classmethod
    def from_row(cls, row: aiosqlite.Row) -> "TerminalNode":
        return cls(
            hash=hexstr_to_bytes32(row["hash"]),
            # generation=row["generation"],
            key=Program.fromhex(row["key"]),
            value=Program.fromhex(row["value"]),
        )


@dataclass(frozen=True)
class InternalNode:
    hash: bytes32
    # generation: int
    left_hash: bytes32
    right_hash: bytes32

    pair: Optional[Tuple[Node, Node]] = None
    atom: None = None

    @classmethod
    def from_row(cls, row: aiosqlite.Row) -> "InternalNode":
        return cls(
            hash=hexstr_to_bytes32(row["hash"]),
            # generation=row["generation"],
            left_hash=hexstr_to_bytes32(row["left"]),
            right_hash=hexstr_to_bytes32(row["right"]),
        )


@dataclass(frozen=True)
class Root:
    tree_id: bytes32
    node_hash: Optional[bytes32]
    generation: int

    @classmethod
    def from_row(cls, row: aiosqlite.Row) -> "Root":
        raw_node_hash = row["node_hash"]
        if raw_node_hash is None:
            node_hash = None
        else:
            node_hash = hexstr_to_bytes32(raw_node_hash)

        return cls(
            tree_id=hexstr_to_bytes32(row["tree_id"]),
            node_hash=node_hash,
            generation=row["generation"],
        )


node_type_to_class: Dict[NodeType, Union[Type[InternalNode], Type[TerminalNode]]] = {
    NodeType.INTERNAL: InternalNode,
    NodeType.TERMINAL: TerminalNode,
}
