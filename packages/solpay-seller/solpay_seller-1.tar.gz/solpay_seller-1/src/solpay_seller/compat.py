from __future__ import annotations

from typing import Any, Optional, Type, TypeVar, cast

try:
  from pydantic import BaseModel as _PydanticBaseModel
  from pydantic import ConfigDict as _ConfigDict

  HAS_PYDANTIC = True
except Exception:  # pragma: no cover
  _PydanticBaseModel = object  # type: ignore
  _ConfigDict = dict  # type: ignore
  HAS_PYDANTIC = False

BaseModel = _PydanticBaseModel
ConfigDict = _ConfigDict

T = TypeVar("T")


def parse_model(model: Type[T], data: Any) -> Optional[T]:
  """
  Parse data into a pydantic model if pydantic is installed.
  Returns None if pydantic is unavailable.
  """
  if not HAS_PYDANTIC:
    return None
  # pydantic v2: model_validate
  m = cast(Any, model)
  if hasattr(m, "model_validate"):
    return cast(T, m.model_validate(data))
  return cast(T, m.parse_obj(data))

