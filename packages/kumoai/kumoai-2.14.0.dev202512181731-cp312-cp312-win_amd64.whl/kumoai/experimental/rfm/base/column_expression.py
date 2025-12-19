from dataclasses import dataclass
from typing import Any, TypeAlias

from kumoapi.typing import Dtype

from kumoai.mixin import CastMixin


@dataclass(frozen=True)
class ColumnExpressionSpec(CastMixin):
    name: str
    expr: str
    dtype: Dtype | None = None


ColumnExpressionType: TypeAlias = ColumnExpressionSpec | dict[str, Any]
