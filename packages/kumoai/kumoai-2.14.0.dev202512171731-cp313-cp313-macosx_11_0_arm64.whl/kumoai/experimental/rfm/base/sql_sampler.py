from abc import abstractmethod
from typing import Literal

import numpy as np
import pandas as pd

from kumoai.experimental.rfm.base import Sampler, SamplerOutput


class SQLSampler(Sampler):
    def _sample_subgraph(
        self,
        entity_table_name: str,
        entity_pkey: pd.Series,
        anchor_time: pd.Series | Literal['entity'],
        columns_dict: dict[str, set[str]],
        num_neighbors: list[int],
    ) -> SamplerOutput:

        df, batch = self._by_pkey(
            table_name=entity_table_name,
            pkey=entity_pkey,
            columns=columns_dict[entity_table_name],
        )
        if len(batch) != len(entity_pkey):
            mask = np.ones(len(entity_pkey), dtype=bool)
            mask[batch] = False
            raise KeyError(f"The primary keys "
                           f"{entity_pkey.iloc[mask].tolist()} do not exist "
                           f"in the '{entity_table_name}' table")

        perm = batch.argsort()
        batch = batch[perm]
        df = df.iloc[perm].reset_index(drop=True)

        if not isinstance(anchor_time, pd.Series):
            time_column = self.time_column_dict[entity_table_name]
            anchor_time = df[time_column]

        return SamplerOutput(
            anchor_time=anchor_time.astype(int).to_numpy(),
            df_dict={entity_table_name: df},
            inverse_dict={},
            batch_dict={entity_table_name: batch},
            num_sampled_nodes_dict={entity_table_name: [len(batch)]},
            row_dict={},
            col_dict={},
            num_sampled_edges_dict={},
        )

    # Abstract Methods ########################################################

    @abstractmethod
    def _by_pkey(
        self,
        table_name: str,
        pkey: pd.Series,
        columns: set[str],
    ) -> tuple[pd.DataFrame, np.ndarray]:
        pass
