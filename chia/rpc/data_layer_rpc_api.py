import dataclasses
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple, Type
from pathlib import Path

import desert
import marshmallow
import marshmallow.fields
from typing_extensions import Protocol

from chia.data_layer.data_layer import DataLayer
from chia.data_layer.data_layer_util import Side, Subscription

from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.byte_types import hexstr_to_bytes

# todo input assertions for all rpc's
from chia.util.ints import uint64
from chia.util.streamable import recurse_jsonify


class BytesField(marshmallow.fields.Field):
    def _serialize(self, value: bytes, attr: str, obj: object, **kwargs: object) -> str:
        return value.hex()

    def _deserialize(
        self,
        value: str,
        attr: Optional[str],
        data: Optional[Mapping[str, object]],
        **kwargs: object,
    ) -> bytes:
        try:
            return hexstr_to_bytes(value)
        except ValueError as error:
            raise marshmallow.ValidationError("Must be a valid hexadecimal string") from error

    def _jsonschema_type_mapping(self) -> Dict[str, str]:
        return {
            "type": "string",
        }


class Bytes32Field(marshmallow.fields.Field):
    def _serialize(self, value: bytes32, attr: str, obj: object, **kwargs: object) -> str:
        return value.hex()

    def _deserialize(
        self,
        value: str,
        attr: Optional[str],
        data: Optional[Mapping[str, object]],
        **kwargs: object,
    ) -> bytes32:
        try:
            return bytes32.from_hexstr(value)
        except ValueError as error:
            raise marshmallow.ValidationError("Must be a valid hexadecimal string of length 32 bytes.") from error

    def _jsonschema_type_mapping(self) -> Dict[str, str]:
        return {
            "type": "string",
        }


# TODO: implement a proper user-provided registry
desert._make._native_to_marshmallow[bytes] = BytesField
desert._make._native_to_marshmallow[bytes32] = Bytes32Field


@dataclasses.dataclass(frozen=True)
class KeyValue:
    key: bytes
    value: bytes


@dataclasses.dataclass(frozen=True)
class OfferStore:
    store_id: bytes32
    inclusions: Tuple[KeyValue, ...]


@dataclasses.dataclass(frozen=True)
class Layer:
    other_hash_side: Side
    other_hash: bytes32
    # TODO: redundant?
    combined_hash: bytes32


@dataclasses.dataclass(frozen=True)
class MakeOfferRequest:
    maker: Tuple[OfferStore, ...]
    taker: Tuple[OfferStore, ...]


@dataclasses.dataclass(frozen=True)
class Proof:
    key: bytes
    value: bytes
    # TODO: redundant?
    node_hash: bytes32
    layers: Tuple[Layer, ...]


@dataclasses.dataclass(frozen=True)
class StoreProofs:
    store_id: bytes32
    proofs: Tuple[Proof, ...]


@dataclasses.dataclass(frozen=True)
class Offer:
    # TODO: enforce bech32m and prefix?
    offer_id: str
    offer: bytes
    taker: Tuple[OfferStore, ...]
    maker: Tuple[StoreProofs, ...]


@dataclasses.dataclass(frozen=True)
class MakeOfferResponse:
    success: bool
    offer: Offer


@dataclasses.dataclass(frozen=True)
class TakeOfferRequest:
    offer: Offer


@dataclasses.dataclass(frozen=True)
class TakeOfferResponse:
    success: bool
    transaction_id: bytes32


class UnboundRoute(Protocol):
    async def __call__(self, request: Dict[str, Any]) -> Dict[str, object]:
        pass


class UnboundMarshalledRoute(Protocol):
    # Ignoring pylint complaint about the name of the first argument since this is a
    # special case.
    async def __call__(protocol_self, self: Any, request: Any) -> object:  # pylint: disable=E0213
        pass


class RouteDecorator(Protocol):
    def __call__(self, route: UnboundMarshalledRoute) -> UnboundRoute:
        pass


# TODO: move elsewhere if this is going to survive
def marshal() -> RouteDecorator:
    def decorator(route: UnboundMarshalledRoute) -> UnboundRoute:
        from typing import get_type_hints

        hints = get_type_hints(route)
        request_class: Type[object] = hints["request"]
        response_class: Type[object] = hints["return"]

        async def wrapper(self: object, request: Dict[str, object]) -> Dict[str, object]:
            request_schema = desert.schema(request_class)
            marshalled_request = request_schema.load(request)

            response = await route(self, request=marshalled_request)

            response_schema = desert.schema(response_class)
            return response_schema.dump(response)  # type: ignore[no-any-return]

        # type ignoring since mypy is having issues with bound vs. unbound methods
        return wrapper  # type: ignore[return-value]

    return decorator


def process_change(change: Dict[str, Any]) -> Dict[str, Any]:
    # TODO: A full class would likely be nice for this so downstream doesn't
    #       have to deal with maybe-present attributes or Dict[str, Any] hints.
    reference_node_hash = change.get("reference_node_hash")
    if reference_node_hash is not None:
        reference_node_hash = bytes32(hexstr_to_bytes(reference_node_hash))

    side = change.get("side")
    if side is not None:
        side = Side(side)

    value = change.get("value")
    if value is not None:
        value = hexstr_to_bytes(value)

    return {
        **change,
        "key": hexstr_to_bytes(change["key"]),
        "value": value,
        "reference_node_hash": reference_node_hash,
        "side": side,
    }


def get_fee(config: Dict[str, Any], request: Dict[str, Any]) -> uint64:
    fee = request.get("fee")
    if fee is None:
        config_fee = config.get("fee", 0)
        return uint64(config_fee)
    return uint64(fee)


class DataLayerRpcApi:
    # TODO: other RPC APIs do not accept a wallet and the service start does not expect to provide one
    def __init__(self, data_layer: DataLayer):  # , wallet: DataLayerWallet):
        self.service: DataLayer = data_layer
        self.service_name = "chia_data_layer"

    def get_routes(self) -> Dict[str, Callable[[Any], Any]]:
        return {
            "/create_data_store": self.create_data_store,
            "/get_owned_stores": self.get_owned_stores,
            "/batch_update": self.batch_update,
            "/get_value": self.get_value,
            "/get_keys_values": self.get_keys_values,
            "/get_ancestors": self.get_ancestors,
            "/get_root": self.get_root,
            "/get_local_root": self.get_local_root,
            "/get_roots": self.get_roots,
            "/delete_key": self.delete_key,
            "/insert": self.insert,
            "/subscribe": self.subscribe,
            "/unsubscribe": self.unsubscribe,
            "/subscriptions": self.subscriptions,
            "/get_kv_diff": self.get_kv_diff,
            "/get_root_history": self.get_root_history,
            "/add_missing_files": self.add_missing_files,
            "/make_offer": self.make_offer,
            "/take_offer": self.take_offer,
        }

    async def create_data_store(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if self.service is None:
            raise Exception("Data layer not created")
        fee = get_fee(self.service.config, request)
        txs, value = await self.service.create_store(uint64(fee))
        return {"txs": txs, "id": value.hex()}

    async def get_owned_stores(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if self.service is None:
            raise Exception("Data layer not created")
        singleton_records = await self.service.get_owned_stores()
        return {"store_ids": [singleton.launcher_id.hex() for singleton in singleton_records]}

    async def get_value(self, request: Dict[str, Any]) -> Dict[str, Any]:
        store_id = bytes32.from_hexstr(request["id"])
        key = hexstr_to_bytes(request["key"])
        if self.service is None:
            raise Exception("Data layer not created")
        value = await self.service.get_value(store_id=store_id, key=key)
        hex = None
        if value is not None:
            hex = value.hex()
        return {"value": hex}

    async def get_keys_values(self, request: Dict[str, Any]) -> Dict[str, Any]:
        store_id = bytes32(hexstr_to_bytes(request["id"]))
        root_hash = request.get("root_hash")
        if root_hash is not None:
            root_hash = bytes32.from_hexstr(root_hash)
        if self.service is None:
            raise Exception("Data layer not created")
        res = await self.service.get_keys_values(store_id, root_hash)
        json_nodes = []
        for node in res:
            json = recurse_jsonify(dataclasses.asdict(node))
            json_nodes.append(json)
        return {"keys_values": json_nodes}

    async def get_ancestors(self, request: Dict[str, Any]) -> Dict[str, Any]:
        store_id = bytes32(hexstr_to_bytes(request["id"]))
        node_hash = bytes32.from_hexstr(request["hash"])
        if self.service is None:
            raise Exception("Data layer not created")
        value = await self.service.get_ancestors(node_hash, store_id)
        return {"ancestors": value}

    async def batch_update(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        id  - the id of the store we are operating on
        changelist - a list of changes to apply on store
        """
        fee = get_fee(self.service.config, request)
        changelist = [process_change(change) for change in request["changelist"]]
        store_id = bytes32(hexstr_to_bytes(request["id"]))
        # todo input checks
        if self.service is None:
            raise Exception("Data layer not created")
        transaction_record = await self.service.batch_update(store_id, changelist, uint64(fee))
        if transaction_record is None:
            raise Exception(f"Batch update failed for: {store_id}")
        return {"tx_id": transaction_record.name}

    async def insert(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        rows_to_add a list of clvm objects as bytes to add to talbe
        rows_to_remove a list of row hashes to remove
        """
        fee = get_fee(self.service.config, request)
        key = hexstr_to_bytes(request["key"])
        value = hexstr_to_bytes(request["value"])
        store_id = bytes32(hexstr_to_bytes(request["id"]))
        # todo input checks
        if self.service is None:
            raise Exception("Data layer not created")
        changelist = [{"action": "insert", "key": key, "value": value}]
        transaction_record = await self.service.batch_update(store_id, changelist, uint64(fee))
        return {"tx_id": transaction_record.name}

    async def delete_key(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        rows_to_add a list of clvm objects as bytes to add to talbe
        rows_to_remove a list of row hashes to remove
        """
        fee = get_fee(self.service.config, request)
        key = hexstr_to_bytes(request["key"])
        store_id = bytes32(hexstr_to_bytes(request["id"]))
        # todo input checks
        if self.service is None:
            raise Exception("Data layer not created")
        changelist = [{"action": "delete", "key": key}]
        transaction_record = await self.service.batch_update(store_id, changelist, uint64(fee))
        return {"tx_id": transaction_record.name}

    async def get_root(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """get hash of latest tree root"""
        store_id = bytes32(hexstr_to_bytes(request["id"]))
        # todo input checks
        if self.service is None:
            raise Exception("Data layer not created")
        rec = await self.service.get_root(store_id)
        if rec is None:
            raise Exception(f"Failed to get root for {store_id.hex()}")
        return {"hash": rec.root, "confirmed": rec.confirmed, "timestamp": rec.timestamp}

    async def get_local_root(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """get hash of latest tree root saved in our local datastore"""
        store_id = bytes32(hexstr_to_bytes(request["id"]))
        # todo input checks
        if self.service is None:
            raise Exception("Data layer not created")
        res = await self.service.get_local_root(store_id)
        return {"hash": res}

    async def get_roots(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        get state hashes for a list of roots
        """
        store_ids = request["ids"]
        # todo input checks
        if self.service is None:
            raise Exception("Data layer not created")
        roots = []
        for id in store_ids:
            id_bytes = bytes32.from_hexstr(id)
            rec = await self.service.get_root(id_bytes)
            if rec is not None:
                roots.append({"id": id_bytes, "hash": rec.root, "confirmed": rec.confirmed, "timestamp": rec.timestamp})
        return {"root_hashes": roots}

    async def subscribe(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        subscribe to singleton
        """
        store_id = request.get("id")
        if store_id is None:
            raise Exception("missing store id in request")

        if self.service is None:
            raise Exception("Data layer not created")
        store_id_bytes = bytes32.from_hexstr(store_id)
        urls = request["urls"]
        await self.service.subscribe(store_id=store_id_bytes, urls=urls)
        return {}

    async def unsubscribe(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        unsubscribe from singleton
        """
        store_id = request.get("id")
        if store_id is None:
            raise Exception("missing store id in request")
        if self.service is None:
            raise Exception("Data layer not created")
        store_id_bytes = bytes32.from_hexstr(store_id)
        await self.service.unsubscribe(store_id_bytes)
        return {}

    async def subscriptions(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        List current subscriptions
        """
        if self.service is None:
            raise Exception("Data layer not created")
        subscriptions: List[Subscription] = await self.service.get_subscriptions()
        return {"store_ids": [sub.tree_id.hex() for sub in subscriptions]}

    async def add_missing_files(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        complete the data server files.
        """
        if "ids" in request:
            store_ids = request["ids"]
            ids_bytes = [bytes32.from_hexstr(id) for id in store_ids]
        else:
            subscriptions: List[Subscription] = await self.service.get_subscriptions()
            ids_bytes = [subscription.tree_id for subscription in subscriptions]
        override = request.get("override", False)
        foldername: Optional[Path] = None
        if "foldername" in request:
            foldername = Path(request["foldername"])
        for tree_id in ids_bytes:
            await self.service.add_missing_files(tree_id, override, foldername)
        return {}

    async def get_root_history(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        get history of state hashes for a store
        """
        if self.service is None:
            raise Exception("Data layer not created")
        store_id = request["id"]
        id_bytes = bytes32.from_hexstr(store_id)
        records = await self.service.get_root_history(id_bytes)
        res: List[Dict[str, Any]] = []
        for rec in records:
            res.insert(0, {"root_hash": rec.root, "confirmed": rec.confirmed, "timestamp": rec.timestamp})
        return {"root_history": res}

    async def get_kv_diff(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        get kv diff between two root hashes
        """
        if self.service is None:
            raise Exception("Data layer not created")
        store_id = request["id"]
        id_bytes = bytes32.from_hexstr(store_id)
        hash_1 = request["hash_1"]
        hash_1_bytes = bytes32.from_hexstr(hash_1)
        hash_2 = request["hash_2"]
        hash_2_bytes = bytes32.from_hexstr(hash_2)
        records = await self.service.get_kv_diff(id_bytes, hash_1_bytes, hash_2_bytes)
        res: List[Dict[str, Any]] = []
        for rec in records:
            res.insert(0, {"type": rec.type.name, "key": rec.key.hex(), "value": rec.value.hex()})
        return {"diff": res}

    @marshal()
    async def make_offer(self, request: MakeOfferRequest) -> MakeOfferResponse:
        return MakeOfferResponse(
            success=True,
            offer=Offer(
                offer_id="",
                offer=b"",
                taker=(),
                maker=(),
            ),
        )

    @marshal()
    async def take_offer(self, request: TakeOfferRequest) -> TakeOfferResponse:
        return TakeOfferResponse(success=True, transaction_id=bytes32(b"\0" * 32))
