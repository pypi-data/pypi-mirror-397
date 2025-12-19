import json
from collections.abc import Iterator
from contextlib import contextmanager

import numpy as np
import pandas as pd
import pyarrow as pa
from kumoapi.pquery import ValidatedPredictiveQuery

from kumoai.experimental.rfm.backend.snow import Connection
from kumoai.experimental.rfm.base import SQLSampler
from kumoai.experimental.rfm.pquery import PQueryPandasExecutor
from kumoai.utils import quote_ident


@contextmanager
def paramstyle(connection: Connection, style: str = 'qmark') -> Iterator[None]:
    _style = connection._paramstyle
    connection._paramstyle = style
    yield
    connection._paramstyle = _style


class SnowSampler(SQLSampler):
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
                      f"FROM {self.fqn_dict[table_name]}")
            selects.append(select)
        sql = "\nUNION ALL\n".join(selects)

        out_dict: dict[str, tuple[pd.Timestamp, pd.Timestamp]] = {}
        with paramstyle(self._connection), self._connection.cursor() as cursor:
            cursor.execute(sql, table_names)
            rows = cursor.fetchall()
        for table_name, _min, _max in rows:
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
        # NOTE Snowflake does support `SEED` only as part of `SYSTEM` sampling.
        num_rows = min(num_rows, 1_000_000)  # Snowflake's upper limit.

        filters: list[str] = []
        primary_key = self.primary_key_dict[table_name]
        if self.source_table_dict[table_name][primary_key].is_nullable:
            filters.append(f" {quote_ident(primary_key)} IS NOT NULL")
        time_column = self.time_column_dict.get(table_name)
        if (time_column is not None and
                self.source_table_dict[table_name][time_column].is_nullable):
            filters.append(f" {quote_ident(time_column)} IS NOT NULL")

        sql = (f"SELECT {', '.join(quote_ident(col) for col in columns)}\n"
               f"FROM {self.fqn_dict[table_name]}\n"
               f"SAMPLE ROW ({num_rows} ROWS)")
        if len(filters) > 0:
            sql += f"\nWHERE{' AND'.join(filters)}"

        with self._connection.cursor() as cursor:
            # NOTE This may return duplicate primary keys. This is okay.
            cursor.execute(sql)
            table = cursor.fetch_arrow_all()

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

        # NOTE For Snowflake, we execute everything at once to pay minimal
        # query initialization costs.
        index = np.concatenate([train_index, test_index])
        time = pd.concat([train_time, test_time], axis=0, ignore_index=True)

        entity_df = entity_df.iloc[index].reset_index(drop=True)

        feat_dict: dict[str, pd.DataFrame] = {query.entity_table: entity_df}
        time_dict: dict[str, pd.Series] = {}
        time_column = self.time_column_dict.get(query.entity_table)
        if time_column in columns_dict[query.entity_table]:
            time_dict[query.entity_table] = entity_df[time_column]
        batch_dict: dict[str, np.ndarray] = {
            query.entity_table: np.arange(len(entity_df)),
        }
        for edge_type, (min_offset, max_offset) in time_offset_dict.items():
            table_name, fkey, _ = edge_type
            feat_dict[table_name], batch_dict[table_name] = self._by_time(
                table_name=table_name,
                fkey=fkey,
                pkey=entity_df[self.primary_key_dict[query.entity_table]],
                anchor_time=time,
                min_offset=min_offset,
                max_offset=max_offset,
                columns=columns_dict[table_name],
            )
            time_column = self.time_column_dict.get(table_name)
            if time_column in columns_dict[table_name]:
                time_dict[table_name] = feat_dict[table_name][time_column]

        y, mask = PQueryPandasExecutor().execute(
            query=query,
            feat_dict=feat_dict,
            time_dict=time_dict,
            batch_dict=batch_dict,
            anchor_time=time,
            num_forecasts=query.num_forecasts,
        )

        train_mask = mask[:len(train_index)]
        test_mask = mask[len(train_index):]

        boundary = int(train_mask.sum())
        train_y = y.iloc[:boundary]
        test_y = y.iloc[boundary:].reset_index(drop=True)

        return train_y, train_mask, test_y, test_mask

    def _by_pkey(
        self,
        table_name: str,
        pkey: pd.Series,
        columns: set[str],
    ) -> tuple[pd.DataFrame, np.ndarray]:

        pkey_name = self.primary_key_dict[table_name]
        source_table = self.source_table_dict[table_name]

        payload = json.dumps(list(pkey))

        sql = ("WITH TMP as (\n"
               "  SELECT\n"
               "    f.index as BATCH,\n")
        if source_table[pkey_name].dtype.is_int():
            sql += "    f.value::NUMBER as ID\n"
        elif source_table[pkey_name].dtype.is_float():
            sql += "    f.value::FLOAT as ID\n"
        else:
            sql += "    f.value::VARCHAR as ID\n"
        sql += (f"  FROM TABLE(FLATTEN(INPUT => PARSE_JSON(?))) f\n"
                f")\n"
                f"SELECT TMP.BATCH as __BATCH__, "
                f"{', '.join('ENT.' + quote_ident(col) for col in columns)}\n"
                f"FROM TMP\n"
                f"JOIN {self.fqn_dict[table_name]} ENT\n"
                f"  ON ENT.{quote_ident(pkey_name)} = TMP.ID")

        with paramstyle(self._connection), self._connection.cursor() as cursor:
            cursor.execute(sql, (payload, ))
            table = cursor.fetch_arrow_all()

        # Remove any duplicated primary keys in post-processing:
        tmp = table.append_column('__TMP__', pa.array(range(len(table))))
        gb = tmp.group_by('__BATCH__').aggregate([('__TMP__', 'min')])
        table = table.take(gb['__TMP___min'])

        batch = table['__BATCH__'].cast(pa.int64()).to_numpy()
        table = table.remove_column(table.schema.get_field_index('__BATCH__'))

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

        end_time = anchor_time + max_offset
        end_time = end_time.dt.strftime("%Y-%m-%d %H:%M:%S")
        if min_offset is not None:
            start_time = anchor_time + min_offset
            start_time = start_time.dt.strftime("%Y-%m-%d %H:%M:%S")
            payload = json.dumps(list(zip(pkey, end_time, start_time)))
        else:
            payload = json.dumps(list(zip(pkey, end_time)))

        # Based on benchmarking, JSON payload is the fastest way to query by
        # custom indices (compared to large `IN` clauses or temporary tables):
        source_table = self.source_table_dict[table_name]
        time_column = self.time_column_dict[table_name]
        sql = ("WITH TMP as (\n"
               "  SELECT\n"
               "    f.index as BATCH,\n")
        if source_table[fkey].dtype.is_int():
            sql += "    f.value[0]::NUMBER as ID,\n"
        elif source_table[fkey].dtype.is_float():
            sql += "    f.value[0]::FLOAT as ID,\n"
        else:
            sql += "    f.value[0]::VARCHAR as ID,\n"
        sql += "    f.value[1]::TIMESTAMP_NTZ as END_TIME"
        if min_offset is not None:
            sql += ",\n    f.value[2]::TIMESTAMP_NTZ as START_TIME"
        sql += (f"\n"
                f"  FROM TABLE(FLATTEN(INPUT => PARSE_JSON(?))) f\n"
                f")\n"
                f"SELECT TMP.BATCH as __BATCH__, "
                f"{', '.join('FACT.' + quote_ident(col) for col in columns)}\n"
                f"FROM TMP\n"
                f"JOIN {self.fqn_dict[table_name]} FACT\n"
                f"  ON FACT.{quote_ident(fkey)} = TMP.ID\n"
                f" AND FACT.{quote_ident(time_column)} <= TMP.END_TIME")
        if min_offset is not None:
            sql += f"\n AND FACT.{quote_ident(time_column)} > TMP.START_TIME"

        with paramstyle(self._connection), self._connection.cursor() as cursor:
            cursor.execute(sql, (payload, ))
            table = cursor.fetch_arrow_all()

        batch = table['__BATCH__'].cast(pa.int64()).to_numpy()
        table = table.remove_column(table.schema.get_field_index('__BATCH__'))

        return self._sanitize(table_name, table), batch

    def _sanitize(self, table_name: str, table: pa.table) -> pd.DataFrame:
        return table.to_pandas(types_mapper=pd.ArrowDtype)
