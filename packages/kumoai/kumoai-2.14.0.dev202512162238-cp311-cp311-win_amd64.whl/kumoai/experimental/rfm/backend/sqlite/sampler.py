import warnings
from collections import defaultdict
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pyarrow as pa
from kumoapi.pquery import ValidatedPredictiveQuery
from kumoapi.typing import Stype

from kumoai.experimental.rfm.backend.sqlite import SQLiteTable
from kumoai.experimental.rfm.base import SQLSampler
from kumoai.experimental.rfm.pquery import PQueryPandasExecutor
from kumoai.utils import ProgressLogger, quote_ident

if TYPE_CHECKING:
    from kumoai.experimental.rfm import Graph


class SQLiteSampler(SQLSampler):
    def __init__(
        self,
        graph: 'Graph',
        verbose: bool | ProgressLogger = True,
        optimize: bool = False,
    ) -> None:
        super().__init__(graph=graph, verbose=verbose)

        for table in graph.tables.values():
            assert isinstance(table, SQLiteTable)
            self._connection = table._connection

        if optimize:
            with self._connection.cursor() as cursor:
                cursor.execute("PRAGMA temp_store = MEMORY")
                cursor.execute("PRAGMA cache_size = -2000000")  # 2 GB

        # Collect database indices to speed-up sampling:
        index_dict: dict[str, set[tuple[str, ...]]] = defaultdict(set)
        for table_name, primary_key in self.primary_key_dict.items():
            source_table = self.source_table_dict[table_name]
            if not source_table[primary_key].is_unique_key:
                index_dict[table_name].add((primary_key, ))
        for src_table_name, foreign_key, _ in graph.edges:
            source_table = self.source_table_dict[src_table_name]
            if source_table[foreign_key].is_unique_key:
                pass
            elif time_column := self.time_column_dict.get(src_table_name):
                index_dict[src_table_name].add((foreign_key, time_column))
            else:
                index_dict[src_table_name].add((foreign_key, ))

        # Only maintain missing indices:
        with self._connection.cursor() as cursor:
            for table_name in list(index_dict.keys()):
                indices = index_dict[table_name]
                sql = f"PRAGMA index_list({quote_ident(table_name)})"
                cursor.execute(sql)
                for _, index_name, *_ in cursor.fetchall():
                    sql = f"PRAGMA index_info({quote_ident(index_name)})"
                    cursor.execute(sql)
                    index = tuple(info[2] for info in sorted(
                        cursor.fetchall(), key=lambda x: x[0]))
                    indices.discard(index)
                if len(indices) == 0:
                    del index_dict[table_name]

        num = sum(len(indices) for indices in index_dict.values())
        index_repr = '1 index' if num == 1 else f'{num} indices'
        num = len(index_dict)
        table_repr = '1 table' if num == 1 else f'{num} tables'

        if optimize and len(index_dict) > 0:
            if not isinstance(verbose, ProgressLogger):
                verbose = ProgressLogger.default(
                    msg="Optimizing SQLite database",
                    verbose=verbose,
                )

            with verbose as logger, self._connection.cursor() as cursor:
                for table_name, indices in index_dict.items():
                    for index in indices:
                        name = f"kumo_index_{table_name}_{'_'.join(index)}"
                        columns = ', '.join(quote_ident(v) for v in index)
                        columns += ' DESC' if len(index) > 1 else ''
                        sql = (f"CREATE INDEX IF NOT EXISTS {name}\n"
                               f"ON {quote_ident(table_name)}({columns})")
                        cursor.execute(sql)
                self._connection.commit()
                logger.log(f"Created {index_repr} in {table_repr}")

        elif len(index_dict) > 0:
            warnings.warn(f"Missing {index_repr} in {table_repr} for optimal "
                          f"database querying. For improving runtime, we "
                          f"strongly suggest to create these indices by "
                          f"instantiating KumoRFM via "
                          f"`KumoRFM(graph, optimize=True)`.")

    def _get_min_max_time_dict(
        self,
        table_names: list[str],
    ) -> dict[str, tuple[pd.Timestamp, pd.Timestamp]]:
        selects: list[str] = []
        for table_name in table_names:
            time_column = self.time_column_dict[table_name]
            select = (f"SELECT\n"
                      f"  ? as table_name,\n"
                      f"  MIN({quote_ident(time_column)}) as min_date,\n"
                      f"  MAX({quote_ident(time_column)}) as max_date\n"
                      f"FROM {quote_ident(table_name)}")
            selects.append(select)
        sql = "\nUNION ALL\n".join(selects)

        out_dict: dict[str, tuple[pd.Timestamp, pd.Timestamp]] = {}
        with self._connection.cursor() as cursor:
            cursor.execute(sql, table_names)
            for table_name, _min, _max in cursor.fetchall():
                out_dict[table_name] = (
                    pd.Timestamp.max if _min is None else pd.Timestamp(_min),
                    pd.Timestamp.min if _max is None else pd.Timestamp(_max),
                )
        return out_dict

    def _sample_entity_table(
        self,
        table_name: str,
        columns: set[str],
        num_rows: int,
        random_seed: int | None = None,
    ) -> pd.DataFrame:
        # NOTE SQLite does not natively support passing a `random_seed`.

        filters: list[str] = []
        primary_key = self.primary_key_dict[table_name]
        if self.source_table_dict[table_name][primary_key].is_nullable:
            filters.append(f" {quote_ident(primary_key)} IS NOT NULL")
        time_column = self.time_column_dict.get(table_name)
        if (time_column is not None and
                self.source_table_dict[table_name][time_column].is_nullable):
            filters.append(f" {quote_ident(time_column)} IS NOT NULL")

        # TODO Make this query more efficient - it does full table scan.
        sql = (f"SELECT {', '.join(quote_ident(col) for col in columns)}\n"
               f"FROM {quote_ident(table_name)}")
        if len(filters) > 0:
            sql += f"\nWHERE{' AND'.join(filters)}"
        sql += f"\nORDER BY RANDOM() LIMIT {num_rows}"

        with self._connection.cursor() as cursor:
            # NOTE This may return duplicate primary keys. This is okay.
            cursor.execute(sql)
            table = cursor.fetch_arrow_table()

        return self._sanitize(table_name, table)

    def _sample_target(
        self,
        query: ValidatedPredictiveQuery,
        entity_df: pd.DataFrame,
        train_index: np.ndarray,
        train_time: pd.Series,
        num_train_examples: int,
        test_index: np.ndarray,
        test_time: pd.Series,
        num_test_examples: int,
        columns_dict: dict[str, set[str]],
        time_offset_dict: dict[
            tuple[str, str, str],
            tuple[pd.DateOffset | None, pd.DateOffset],
        ],
    ) -> tuple[pd.Series, np.ndarray, pd.Series, np.ndarray]:
        train_y, train_mask = self._sample_target_set(
            query=query,
            entity_df=entity_df,
            index=train_index,
            anchor_time=train_time,
            num_examples=num_train_examples,
            columns_dict=columns_dict,
            time_offset_dict=time_offset_dict,
        )

        test_y, test_mask = self._sample_target_set(
            query=query,
            entity_df=entity_df,
            index=test_index,
            anchor_time=test_time,
            num_examples=num_test_examples,
            columns_dict=columns_dict,
            time_offset_dict=time_offset_dict,
        )

        return train_y, train_mask, test_y, test_mask

    def _by_pkey(
        self,
        table_name: str,
        pkey: pd.Series,
        columns: set[str],
    ) -> tuple[pd.DataFrame, np.ndarray]:
        pkey_name = self.primary_key_dict[table_name]

        tmp = pa.table([pa.array(pkey)], names=['id'])
        tmp_name = f'tmp_{table_name}_{pkey_name}_{id(tmp)}'

        if self.source_table_dict[table_name][pkey_name].is_unique_key:
            sql = (f"SELECT tmp.rowid - 1 as __batch__, "
                   f"{', '.join('ent.' + quote_ident(c) for c in columns)}\n"
                   f"FROM {quote_ident(tmp_name)} tmp\n"
                   f"JOIN {quote_ident(table_name)} ent\n"
                   f"  ON ent.{quote_ident(pkey_name)} = tmp.id")
        else:
            sql = (f"SELECT tmp.rowid - 1 as __batch__, "
                   f"{', '.join('ent.' + quote_ident(c) for c in columns)}\n"
                   f"FROM {quote_ident(tmp_name)} tmp\n"
                   f"JOIN {quote_ident(table_name)} ent\n"
                   f"  ON ent.rowid = (\n"
                   f"    SELECT rowid FROM {quote_ident(table_name)}\n"
                   f"    WHERE {quote_ident(pkey_name)} == tmp.id\n"
                   f"    LIMIT 1\n"
                   f")")

        with self._connection.cursor() as cursor:
            cursor.adbc_ingest(tmp_name, tmp, mode='replace')
            cursor.execute(sql)
            table = cursor.fetch_arrow_table()

        batch = table['__batch__'].to_numpy()
        table = table.remove_column(table.schema.get_field_index('__batch__'))

        return table.to_pandas(), batch  # TODO Use `self._sanitize`.

    # Helper Methods ##########################################################

    def _by_time(
        self,
        table_name: str,
        fkey: str,
        pkey: pd.Series,
        anchor_time: pd.Series,
        min_offset: pd.DateOffset | None,
        max_offset: pd.DateOffset,
        columns: set[str],
    ) -> tuple[pd.DataFrame, np.ndarray]:
        # NOTE SQLite does not have a native datetime format. Currently, we
        # assume timestamps are given as `TEXT` in `ISO-8601 UTC`:
        tmp = pa.table([pa.array(pkey)], names=['id'])
        end_time = anchor_time + max_offset
        end_time = end_time.dt.strftime("%Y-%m-%d %H:%M:%S")
        tmp = tmp.append_column('end', pa.array(end_time))
        if min_offset is not None:
            start_time = anchor_time + min_offset
            start_time = start_time.dt.strftime("%Y-%m-%d %H:%M:%S")
            tmp = tmp.append_column('start', pa.array(start_time))
        tmp_name = f'tmp_{table_name}_{fkey}_{id(tmp)}'

        time_column = self.time_column_dict[table_name]
        sql = (f"SELECT tmp.rowid - 1 as __batch__, "
               f"{', '.join('fact.' + quote_ident(col) for col in columns)}\n"
               f"FROM {quote_ident(tmp_name)} tmp\n"
               f"JOIN {quote_ident(table_name)} fact\n"
               f"  ON fact.{quote_ident(fkey)} = tmp.id\n"
               f" AND fact.{quote_ident(time_column)} <= tmp.end")
        if min_offset is not None:
            sql += f"\n AND fact.{quote_ident(time_column)} > tmp.start"

        with self._connection.cursor() as cursor:
            cursor.adbc_ingest(tmp_name, tmp, mode='replace')
            cursor.execute(sql)
            table = cursor.fetch_arrow_table()

        batch = table['__batch__'].to_numpy()
        table = table.remove_column(table.schema.get_field_index('__batch__'))

        return self._sanitize(table_name, table), batch

    def _sample_target_set(
        self,
        query: ValidatedPredictiveQuery,
        entity_df: pd.DataFrame,
        index: np.ndarray,
        anchor_time: pd.Series,
        num_examples: int,
        columns_dict: dict[str, set[str]],
        time_offset_dict: dict[
            tuple[str, str, str],
            tuple[pd.DateOffset | None, pd.DateOffset],
        ],
        batch_size: int = 10_000,
    ) -> tuple[pd.Series, np.ndarray]:

        count = 0
        ys: list[pd.Series] = []
        mask = np.full(len(index), False, dtype=bool)
        for start in range(0, len(index), batch_size):
            df = entity_df.iloc[index[start:start + batch_size]]
            time = anchor_time.iloc[start:start + batch_size]

            feat_dict: dict[str, pd.DataFrame] = {query.entity_table: df}
            time_dict: dict[str, pd.Series] = {}
            time_column = self.time_column_dict.get(query.entity_table)
            if time_column in columns_dict[query.entity_table]:
                time_dict[query.entity_table] = df[time_column]
            batch_dict: dict[str, np.ndarray] = {
                query.entity_table: np.arange(len(df)),
            }
            for edge_type, (_min, _max) in time_offset_dict.items():
                table_name, fkey, _ = edge_type
                feat_dict[table_name], batch_dict[table_name] = self._by_time(
                    table_name=table_name,
                    fkey=fkey,
                    pkey=df[self.primary_key_dict[query.entity_table]],
                    anchor_time=time,
                    min_offset=_min,
                    max_offset=_max,
                    columns=columns_dict[table_name],
                )
                time_column = self.time_column_dict.get(table_name)
                if time_column in columns_dict[table_name]:
                    time_dict[table_name] = feat_dict[table_name][time_column]

            y, _mask = PQueryPandasExecutor().execute(
                query=query,
                feat_dict=feat_dict,
                time_dict=time_dict,
                batch_dict=batch_dict,
                anchor_time=anchor_time,
                num_forecasts=query.num_forecasts,
            )
            ys.append(y)
            mask[start:start + batch_size] = _mask

            count += len(y)
            if count >= num_examples:
                break

        if len(ys) == 0:
            y = pd.Series([], dtype=float)
        elif len(ys) == 1:
            y = ys[0]
        else:
            y = pd.concat(ys, axis=0, ignore_index=True)

        return y, mask

    def _sanitize(self, table_name: str, table: pa.table) -> pd.DataFrame:
        df = table.to_pandas(types_mapper=pd.ArrowDtype)

        stype_dict = self.table_stype_dict[table_name]
        for column_name in df.columns:
            if stype_dict.get(column_name) == Stype.timestamp:
                df[column_name] = pd.to_datetime(df[column_name])

        return df
