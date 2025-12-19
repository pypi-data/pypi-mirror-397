from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


Json = Any


class SellerApiKey(TypedDict):
  id: str
  name: str
  keyPrefix: str
  lastUsedAt: Optional[str]
  revokedAt: Optional[str]
  createdAt: str


class CreateSellerApiKeyResponse(SellerApiKey):
  apiKey: str


class WebhookEndpoint(TypedDict, total=False):
  id: str
  url: str
  isActive: bool
  events: List[str]
  createdAt: str
  updatedAt: str
  secret: str


class LotsResponse(TypedDict):
  lots: List[Dict[str, Any]]
  total: int
  page: int
  totalPages: int


class OrdersResponse(TypedDict):
  orders: List[Dict[str, Any]]
  total: int
  page: int
  totalPages: int

