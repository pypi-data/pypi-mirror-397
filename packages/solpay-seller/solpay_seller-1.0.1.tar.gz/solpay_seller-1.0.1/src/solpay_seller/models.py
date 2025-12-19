from __future__ import annotations

from typing import Any, Dict, List, Optional

from .compat import BaseModel, ConfigDict, HAS_PYDANTIC

if HAS_PYDANTIC:
  class _Model(BaseModel):  # type: ignore[misc]
    model_config = ConfigDict(extra="allow")
else:
  class _Model:  # pragma: no cover
    pass


class Me(_Model):
  id: str


class Lot(_Model):
  id: str
  title: str
  type: str
  priceUsd: int
  quantity: Optional[int] = None
  isActive: Optional[bool] = None


class LotsResponse(_Model):
  lots: List[Dict[str, Any]]
  total: int
  page: int
  totalPages: int


class Order(_Model):
  id: str
  status: str
  kind: str
  paymentMethod: Optional[str] = None
  quantity: int
  priceUsd: int
  commissionAmount: Optional[int] = None
  paidAt: Optional[str] = None
  completedAt: Optional[str] = None


class OrdersResponse(_Model):
  orders: List[Dict[str, Any]]
  total: int
  page: int
  totalPages: int


class WebhookEndpoint(_Model):
  id: str
  url: str
  isActive: bool
  events: List[str]
  createdAt: str
  updatedAt: str
  secret: Optional[str] = None

