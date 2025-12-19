import re
from collections.abc import Sequence
from typing import cast

import pandas as pd
from kumoapi.model_plan import MissingType
from kumoapi.typing import Dtype

from kumoai.experimental.rfm.backend.snow import Connection
from kumoai.experimental.rfm.base import (
    ColumnExpressionType,
    DataBackend,
    SourceColumn,
    SourceForeignKey,
    SQLTable,
)
from kumoai.utils import quote_ident


class SnowTable(SQLTable):
    r"""A table backed by a :class:`sqlite` database.

    Args:
        connection: The connection to a :class:`snowflake` database.
        name: The logical name of this table.
        source_name: The physical name of this table in the database. If set to
            ``None``, ``name`` is being used.
        database: The database.
        schema: The schema.
        columns: The selected physical columns of this table.
        column_expressions: The logical columns of this table.
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
        database: str | None = None,
        schema: str | None = None,
        columns: Sequence[str] | None = None,
        column_expressions: Sequence[ColumnExpressionType] | None = None,
        primary_key: MissingType | str | None = MissingType.VALUE,
        time_column: str | None = None,
        end_time_column: str | None = None,
    ) -> None:

        if database is not None and schema is None:
            raise ValueError(f"Unspecified 'schema' for table "
                             f"'{source_name or name}' in database "
                             f"'{database}'")

        self._connection = connection
        self._database = database
        self._schema = schema

        super().__init__(
            name=name,
            source_name=source_name,
            columns=columns,
            column_expressions=column_expressions,
            primary_key=primary_key,
            time_column=time_column,
            end_time_column=end_time_column,
        )

    @property
    def backend(self) -> DataBackend:
        return cast(DataBackend, DataBackend.SNOWFLAKE)

    @property
    def fqn(self) -> str:
        r"""The fully-qualified quoted table name."""
        names: list[str] = []
        if self._database is not None:
            names.append(quote_ident(self._database))
        if self._schema is not None:
            names.append(quote_ident(self._schema))
        return '.'.join(names + [quote_ident(self._source_name)])

    def _get_source_columns(self) -> list[SourceColumn]:
        source_columns: list[SourceColumn] = []
        with self._connection.cursor() as cursor:
            try:
                sql = f"DESCRIBE TABLE {self.fqn}"
                cursor.execute(sql)
            except Exception as e:
                names: list[str] = []
                if self._database is not None:
                    names.append(self._database)
                if self._schema is not None:
                    names.append(self._schema)
                source_name = '.'.join(names + [self._source_name])
                raise ValueError(f"Table '{source_name}' does not exist in "
                                 f"the remote data backend") from e

            for row in cursor.fetchall():
                column, type, _, null, _, is_pkey, is_unique, *_ = row

                type = type.strip().upper()
                if type.startswith('NUMBER'):
                    dtype = Dtype.int
                elif type.startswith('VARCHAR'):
                    dtype = Dtype.string
                elif type == 'FLOAT':
                    dtype = Dtype.float
                elif type == 'BOOLEAN':
                    dtype = Dtype.bool
                elif re.search('DATE|TIMESTAMP', type):
                    dtype = Dtype.date
                else:
                    continue

                source_column = SourceColumn(
                    name=column,
                    dtype=dtype,
                    is_primary_key=is_pkey.strip().upper() == 'Y',
                    is_unique_key=is_unique.strip().upper() == 'Y',
                    is_nullable=null.strip().upper() == 'Y',
                )
                source_columns.append(source_column)

        return source_columns

    def _get_source_foreign_keys(self) -> list[SourceForeignKey]:
        source_fkeys: list[SourceForeignKey] = []
        with self._connection.cursor() as cursor:
            sql = f"SHOW IMPORTED KEYS IN TABLE {self.fqn}"
            cursor.execute(sql)
            for row in cursor.fetchall():
                _, _, _, dst_table, pkey, _, _, _, fkey, *_ = row
                source_fkeys.append(SourceForeignKey(fkey, dst_table, pkey))
        return source_fkeys

    def _get_sample_df(self) -> pd.DataFrame:
        with self._connection.cursor() as cursor:
            columns = [quote_ident(col) for col in self._source_column_dict]
            sql = f"SELECT {', '.join(columns)} FROM {self.fqn} LIMIT 1000"
            cursor.execute(sql)
            table = cursor.fetch_arrow_all()
            return table.to_pandas(types_mapper=pd.ArrowDtype)

    def _get_num_rows(self) -> int | None:
        return None
