from aiosqlite import Row
from typing import List, Optional, Type, TypeVar, Union

import aiosqlite
import dataclasses

from chia.data_layer.data_layer_wallet import SingletonRecord
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.db_wrapper import DBWrapper
from chia.util.ints import uint32, uint64
from chia.wallet.lineage_proof import LineageProof

_T_DataLayerStore = TypeVar("_T_DataLayerStore", bound="DataLayerStore")


# It is unclear how to properly satisfy the generic Row normally, let alone for
# dict-like rows.
def _row_to_singleton_record(row: Row) -> SingletonRecord:  # type: ignore[type-arg]
    return SingletonRecord(
        bytes32(row[0]),
        bytes32(row[1]),
        bytes32(row[2]),
        bytes32(row[3]),
        bool(row[4]),
        uint32(row[5]),
        LineageProof.from_bytes(row[6]),
        uint32(row[7]),
        uint64(row[8]),
    )


class DataLayerStore:
    """
    WalletUserStore keeps track of all user created wallets and necessary smart-contract data
    """

    db_connection: aiosqlite.Connection
    db_wrapper: DBWrapper

    @classmethod
    async def create(cls: Type[_T_DataLayerStore], db_wrapper: DBWrapper) -> _T_DataLayerStore:
        self = cls()

        self.db_wrapper = db_wrapper
        self.db_connection = db_wrapper.db
        await self.db_connection.execute(
            (
                "CREATE TABLE IF NOT EXISTS singleton_records("
                "coin_id blob PRIMARY KEY,"
                " launcher_id blob,"
                " root blob,"
                " inner_puzzle_hash blob,"
                " confirmed tinyint,"
                " confirmed_at_height int,"
                " proof blob,"
                " generation int,"  # This first singleton will be 0, then 1, and so on.  This is handled by the DB.
                " timestamp int)"
            )
        )

        await self.db_connection.execute("CREATE INDEX IF NOT EXISTS coin_id on singleton_records(coin_id)")
        await self.db_connection.execute("CREATE INDEX IF NOT EXISTS launcher_id on singleton_records(launcher_id)")
        await self.db_connection.execute("CREATE INDEX IF NOT EXISTS root on singleton_records(root)")
        await self.db_connection.execute(
            "CREATE INDEX IF NOT EXISTS inner_puzzle_hash on singleton_records(inner_puzzle_hash)"
        )
        await self.db_connection.execute("CREATE INDEX IF NOT EXISTS confirmed_at_height on singleton_records(root)")
        await self.db_connection.execute("CREATE INDEX IF NOT EXISTS generation on singleton_records(generation)")

        await self.db_connection.execute(("CREATE TABLE IF NOT EXISTS launchers(id blob PRIMARY KEY, coin blob)"))

        await self.db_connection.execute("CREATE INDEX IF NOT EXISTS id on launchers(id)")

        await self.db_connection.commit()
        return self

    async def _clear_database(self) -> None:
        cursor = await self.db_connection.execute("DELETE FROM singleton_records")
        await cursor.close()
        await self.db_connection.commit()

    async def add_singleton_record(self, record: SingletonRecord, in_transaction: bool) -> None:
        """
        Store SingletonRecord in DB.
        """

        if not in_transaction:
            await self.db_wrapper.lock.acquire()
        try:
            cursor = await self.db_connection.execute(
                "INSERT OR REPLACE INTO singleton_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record.coin_id,
                    record.launcher_id,
                    record.root,
                    record.inner_puzzle_hash,
                    int(record.confirmed),
                    record.confirmed_at_height,
                    bytes(record.lineage_proof),
                    record.generation,
                    record.timestamp,
                ),
            )
            await cursor.close()
            if not in_transaction:
                await self.db_connection.commit()
        except BaseException:
            if not in_transaction:
                # await self.rebuild_tx_cache()
                pass
            raise
        finally:
            if not in_transaction:
                self.db_wrapper.lock.release()

    async def get_all_singletons_for_launcher(
        self,
        launcher_id: bytes32,
        min_generation: Optional[uint32] = None,
        max_generation: Optional[uint32] = None,
        num_results: Optional[uint32] = None,
    ) -> List[SingletonRecord]:
        """
        Returns stored singletons with a specific launcher ID.
        """
        query_params: List[Union[bytes32, uint32]] = [launcher_id]
        for optional_param in (min_generation, max_generation, num_results):
            if optional_param is not None:
                query_params.append(optional_param)

        cursor = await self.db_connection.execute(
            "SELECT * from singleton_records WHERE launcher_id=? "
            f"{'AND generation >=? ' if min_generation is not None else ''}"
            f"{'AND generation <=? ' if max_generation is not None else ''}"
            "ORDER BY generation DESC"
            f"{' LIMIT ?' if num_results is not None else ''}",
            tuple(query_params),
        )
        rows = await cursor.fetchall()
        await cursor.close()
        records = []

        for row in rows:
            records.append(_row_to_singleton_record(row))

        return records

    async def get_singleton_record(self, coin_id: bytes32) -> Optional[SingletonRecord]:
        """
        Checks DB for SingletonRecord with coin_id: coin_id and returns it.
        """
        # if tx_id in self.tx_record_cache:
        #     return self.tx_record_cache[tx_id]

        cursor = await self.db_connection.execute("SELECT * from singleton_records WHERE coin_id=?", (coin_id,))
        row = await cursor.fetchone()
        await cursor.close()
        if row is not None:
            return _row_to_singleton_record(row)
        return None

    async def get_latest_singleton(
        self, launcher_id: bytes32, only_confirmed: bool = False
    ) -> Optional[SingletonRecord]:
        """
        Checks DB for SingletonRecords with launcher_id: launcher_id and returns the most recent.
        """
        # if tx_id in self.tx_record_cache:
        #     return self.tx_record_cache[tx_id]
        if only_confirmed:
            # get latest confirmed root
            cursor = await self.db_connection.execute(
                "SELECT * from singleton_records WHERE launcher_id=? and confirmed = TRUE "
                "ORDER BY generation DESC LIMIT 1",
                (launcher_id,),
            )
        else:
            cursor = await self.db_connection.execute(
                "SELECT * from singleton_records WHERE launcher_id=? ORDER BY generation DESC LIMIT 1", (launcher_id,)
            )
        row = await cursor.fetchone()
        await cursor.close()
        if row is not None:
            return _row_to_singleton_record(row)
        return None

    async def get_unconfirmed_singletons(self, launcher_id: bytes32) -> List[SingletonRecord]:
        """
        Returns all singletons with a specific launcher id that have not yet been marked confirmed
        """
        cursor = await self.db_connection.execute(
            "SELECT * from singleton_records WHERE launcher_id=? AND confirmed=0", (launcher_id,)
        )
        rows = await cursor.fetchall()
        await cursor.close()
        records = [_row_to_singleton_record(row) for row in rows]

        return records

    async def get_singletons_by_root(self, launcher_id: bytes32, root: bytes32) -> List[SingletonRecord]:
        cursor = await self.db_connection.execute(
            "SELECT * from singleton_records WHERE launcher_id=? AND root=? ORDER BY generation DESC",
            (launcher_id, root),
        )
        rows = await cursor.fetchall()
        await cursor.close()
        records = []

        for row in rows:
            records.append(_row_to_singleton_record(row))

        return records

    async def set_confirmed(self, coin_id: bytes32, height: uint32, timestamp: uint64) -> None:
        """
        Updates singleton record to be confirmed.
        """
        current: Optional[SingletonRecord] = await self.get_singleton_record(coin_id)
        if current is None or current.confirmed_at_height == height:
            return

        await self.add_singleton_record(
            dataclasses.replace(current, confirmed=True, confirmed_at_height=height, timestamp=timestamp), True
        )

    async def delete_singleton_record(self, coin_id: bytes32) -> None:
        c = await self.db_connection.execute("DELETE FROM singleton_records WHERE coin_id=?", (coin_id,))
        await c.close()

    async def delete_singleton_records_by_launcher_id(self, launcher_id: bytes32) -> None:
        c = await self.db_connection.execute("DELETE FROM singleton_records WHERE launcher_id=?", (launcher_id,))
        await c.close()

    async def add_launcher(self, launcher: Coin, in_transaction: bool) -> None:
        """
        Add a new launcher coin's information to the DB
        """
        launcher_bytes: bytes = launcher.parent_coin_info + launcher.puzzle_hash + bytes(launcher.amount)
        if not in_transaction:
            await self.db_wrapper.lock.acquire()
        try:
            cursor = await self.db_connection.execute(
                "INSERT OR REPLACE INTO launchers VALUES (?, ?)",
                (launcher.name(), launcher_bytes),
            )
            await cursor.close()
            if not in_transaction:
                await self.db_connection.commit()
        finally:
            if not in_transaction:
                self.db_wrapper.lock.release()

    async def get_launcher(self, launcher_id: bytes32) -> Optional[Coin]:
        """
        Checks DB for a launcher with the specified ID and returns it.
        """

        cursor = await self.db_connection.execute("SELECT * from launchers WHERE id=?", (launcher_id,))
        row = await cursor.fetchone()
        await cursor.close()
        if row is not None:
            return Coin(bytes32(row[1][0:32]), bytes32(row[1][32:64]), uint64(int.from_bytes(row[1][64:72], "big")))
        return None

    async def get_all_launchers(self) -> List[Coin]:
        """
        Checks DB for all launchers.
        """

        cursor = await self.db_connection.execute("SELECT * from launchers")
        rows = await cursor.fetchall()
        await cursor.close()

        coins: List[Coin] = []
        for row in rows:
            coins.append(
                Coin(bytes32(row[1][0:32]), bytes32(row[1][32:64]), uint64(int.from_bytes(row[1][64:72], "big")))
            )

        return coins

    async def delete_launcher(self, launcher_id: bytes32) -> None:
        c = await self.db_connection.execute("DELETE FROM launchers WHERE id=?", (launcher_id,))
        await c.close()
