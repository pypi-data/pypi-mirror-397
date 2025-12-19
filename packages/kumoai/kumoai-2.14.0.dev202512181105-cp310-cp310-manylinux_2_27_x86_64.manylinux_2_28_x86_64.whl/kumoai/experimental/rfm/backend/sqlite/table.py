import re
import warnings
from collections.abc import Sequence
from typing import cast

import pandas as pd
from kumoapi.model_plan import MissingType
from kumoapi.typing import Dtype

from kumoai.experimental.rfm.backend.sqlite import Connection
from kumoai.experimental.rfm.base import (
    DataBackend,
    SourceColumn,
    SourceForeignKey,
    SQLTable,
)
from kumoai.experimental.rfm.infer import infer_dtype
from kumoai.utils import quote_ident


class SQLiteTable(SQLTable):
    r"""A table backed by a :class:`sqlite` database.

    Args:
        connection: The connection to a :class:`sqlite` database.
        name: The logical name of this table.
        source_name: The physical name of this table in the database. If set to
            ``None``, ``name`` is being used.
        columns: The selected columns of this table.
        primary_key: The name of the primary key of this table, if it exists.
        time_column: The name of the time column of this table, if it exists.
        end_time_column: The name of the end time column of this table, if it
            exists.
    """
    def __init__(
        self,
        connection: Connection,
        name: str,
        source_name: str | None = None,
        columns: Sequence[str] | None = None,
        primary_key: MissingType | str | None = MissingType.VALUE,
        time_column: str | None = None,
        end_time_column: str | None = None,
    ) -> None:

        self._connection = connection

        super().__init__(
            name=name,
            source_name=source_name,
            columns=columns,
            primary_key=primary_key,
            time_column=time_column,
            end_time_column=end_time_column,
        )

    @property
    def backend(self) -> DataBackend:
        return cast(DataBackend, DataBackend.SQLITE)

    def _get_source_columns(self) -> list[SourceColumn]:
        source_columns: list[SourceColumn] = []
        with self._connection.cursor() as cursor:
            sql = f"PRAGMA table_info({self.fqn})"
            cursor.execute(sql)
            columns = cursor.fetchall()

            if len(columns) == 0:
                raise ValueError(f"Table '{self._source_name}' does not exist "
                                 f"in the SQLite database")

            unique_keys: set[str] = set()
            sql = f"PRAGMA index_list({self.fqn})"
            cursor.execute(sql)
            for _, index_name, is_unique, *_ in cursor.fetchall():
                if bool(is_unique):
                    sql = f"PRAGMA index_info({quote_ident(index_name)})"
                    cursor.execute(sql)
                    index = cursor.fetchall()
                    if len(index) == 1:
                        unique_keys.add(index[0][2])

            for _, column, type, notnull, _, is_pkey in columns:
                # Determine column affinity:
                type = type.strip().upper()
                if re.search('INT', type):
                    dtype = Dtype.int
                elif re.search('TEXT|CHAR|CLOB', type):
                    dtype = Dtype.string
                elif re.search('REAL|FLOA|DOUB', type):
                    dtype = Dtype.float
                else:  # NUMERIC affinity.
                    ser = self._sample_df[column]
                    try:
                        dtype = infer_dtype(ser)
                    except Exception:
                        warnings.warn(
                            f"Data type inference for column '{column}' in "
                            f"table '{self.name}' failed. Consider changing "
                            f"the data type of the column in the database or "
                            f"remove this column from this table.")
                        continue

                source_column = SourceColumn(
                    name=column,
                    dtype=dtype,
                    is_primary_key=bool(is_pkey),
                    is_unique_key=column in unique_keys,
                    is_nullable=not bool(is_pkey) and not bool(notnull),
                )
                source_columns.append(source_column)

        return source_columns

    def _get_source_foreign_keys(self) -> list[SourceForeignKey]:
        source_fkeys: list[SourceForeignKey] = []
        with self._connection.cursor() as cursor:
            sql = f"PRAGMA foreign_key_list({self.fqn})"
            cursor.execute(sql)
            for _, _, dst_table, fkey, pkey, *_ in cursor.fetchall():
                source_fkeys.append(SourceForeignKey(fkey, dst_table, pkey))
        return source_fkeys

    def _get_sample_df(self) -> pd.DataFrame:
        with self._connection.cursor() as cursor:
            sql = (f"SELECT * FROM {self.fqn} "
                   f"ORDER BY rowid LIMIT 1000")
            cursor.execute(sql)
            table = cursor.fetch_arrow_table()
            return table.to_pandas(types_mapper=pd.ArrowDtype)

    def _get_num_rows(self) -> int | None:
        return None
