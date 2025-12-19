from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class SellerApiError(RuntimeError):
  status_code: int
  message: str
  details: Any = None
  request_id: Optional[str] = None

  def __str__(self) -> str:
    base = f"SellerApiError({self.status_code}): {self.message}"
    if self.request_id:
      base += f" [request_id={self.request_id}]"
    return base

