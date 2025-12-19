from abc import abstractmethod
from collections import defaultdict
from collections.abc import Sequence
from functools import cached_property
from typing import Any

from kumoapi.model_plan import MissingType

from kumoai.experimental.rfm.base import (
    ColumnExpressionType,
    SourceForeignKey,
    Table,
)
from kumoai.utils import quote_ident


class SQLTable(Table):
    r"""A :class:`SQLTable` specifies a :class:`Table` backed by a SQL
    database.

    Args:
        name: The logical name of this table.
        source_name: The physical name of this table in the database. If set to
            ``None``, ``name`` is being used.
        columns: The selected physical columns of this table.
        column_expressions: The logical columns of this table.
        primary_key: The name of the primary key of this table, if it exists.
        time_column: The name of the time column of this table, if it exists.
        end_time_column: The name of the end time column of this table, if it
            exists.
    """
    def __init__(
        self,
        name: str,
        source_name: str | None = None,
        columns: Sequence[str] | None = None,
        column_expressions: Sequence[ColumnExpressionType] | None = None,
        primary_key: MissingType | str | None = MissingType.VALUE,
        time_column: str | None = None,
        end_time_column: str | None = None,
    ) -> None:

        self._connection: Any
        self._source_name = source_name or name

        super().__init__(
            name=name,
            columns=[],
            primary_key=None,
            time_column=None,
            end_time_column=None,
        )

        if isinstance(primary_key, MissingType):
            primary_key = self._source_primary_key

        # Add column expressions with highest priority:
        self._add_column_expressions(column_expressions or [])

        if columns is None:
            for column_name in self._source_column_dict.keys():
                if column_name not in self:
                    self.add_column(column_name)
        else:
            for column_name in columns:
                self.add_column(column_name)

        if primary_key is not None:
            if primary_key not in self:
                self.add_column(primary_key)
            self.primary_key = primary_key

        if time_column is not None:
            if time_column not in self:
                self.add_column(time_column)
            self.time_column = time_column

        if end_time_column is not None:
            if end_time_column not in self:
                self.add_column(end_time_column)
            self.end_time_column = end_time_column

    @property
    def fqn(self) -> str:
        r"""The fully-qualified quoted source table name."""
        return quote_ident(self._source_name)

    # Column ##################################################################

    def _add_column_expressions(
        self,
        columns: Sequence[ColumnExpressionType],
    ) -> None:
        pass

    # Abstract Methods ########################################################

    @cached_property
    def _source_foreign_key_dict(self) -> dict[str, SourceForeignKey]:
        fkeys = self._get_source_foreign_keys()
        # NOTE Drop all keys that link to multiple keys in the same table since
        # we don't support composite keys yet:
        table_pkeys: dict[str, set[str]] = defaultdict(set)
        for fkey in fkeys:
            table_pkeys[fkey.dst_table].add(fkey.primary_key)
        return {
            fkey.name: fkey
            for fkey in fkeys if len(table_pkeys[fkey.dst_table]) == 1
        }

    @abstractmethod
    def _get_source_foreign_keys(self) -> list[SourceForeignKey]:
        pass
