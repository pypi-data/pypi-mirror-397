from abc import abstractmethod
from collections import defaultdict
from collections.abc import Sequence
from functools import cached_property
from typing import Any

from kumoapi.model_plan import MissingType

from kumoai.experimental.rfm.base import SourceForeignKey, Table
from kumoai.utils import quote_ident


class SQLTable(Table):
    r"""A :class:`SQLTable` specifies a :class:`Table` backed by a SQL
    database.

    Args:
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
        name: str,
        source_name: str | None = None,
        columns: Sequence[str] | None = None,
        primary_key: MissingType | str | None = MissingType.VALUE,
        time_column: str | None = None,
        end_time_column: str | None = None,
    ) -> None:

        self._connection: Any
        self._source_name = source_name or name

        super().__init__(
            name=name,
            columns=columns,
            primary_key=primary_key,
            time_column=time_column,
            end_time_column=end_time_column,
        )

    @property
    def fqn(self) -> str:
        r"""The fully-qualified quoted source table name."""
        return quote_ident(self._source_name)

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
