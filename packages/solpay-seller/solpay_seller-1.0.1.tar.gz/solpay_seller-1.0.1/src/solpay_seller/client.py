from __future__ import annotations

import json
import mimetypes
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from .exceptions import SellerApiError
from .types import OrdersResponse, LotsResponse, Json, WebhookEndpoint
from .compat import HAS_PYDANTIC, parse_model


def _join_url(base_url: str, path: str) -> str:
  base = base_url.rstrip("/")
  p = path if path.startswith("/") else f"/{path}"
  return f"{base}{p}"


@dataclass
class SellerApiClient:
  """
  Minimal, batteries-included client for the public Seller API.

  Auth:
    X-Api-Key: sp_sk_...

  base_url should include `/api`, e.g.:
    https://solpay.one/api
  """

  api_key: str
  base_url: str = "https://solpay.one/api"
  timeout_s: int = 20
  session: Optional[requests.Session] = None

  def __post_init__(self) -> None:
    if not self.api_key or not isinstance(self.api_key, str):
      raise ValueError("api_key is required")
    if self.session is None:
      self.session = requests.Session()
    self.session.headers.update({"X-Api-Key": self.api_key})

  def request(self, method: str, path: str, json_body: Optional[dict] = None) -> Json:
    url = _join_url(self.base_url, path)
    headers: Dict[str, str] = {}
    data: Optional[str] = None

    if json_body is not None:
      headers["content-type"] = "application/json"
      data = json.dumps(json_body)

    resp = self.session.request(  # type: ignore[union-attr]
      method=method.upper(),
      url=url,
      headers=headers,
      data=data,
      timeout=self.timeout_s,
    )

    request_id = resp.headers.get("x-request-id") or resp.headers.get("x-requestid")

    content_type = (resp.headers.get("content-type") or "").lower()
    is_json = content_type.startswith("application/json")

    if not resp.ok:
      details: Any
      message = resp.reason
      if is_json:
        try:
          details = resp.json()
          if isinstance(details, dict) and "message" in details:
            msg = details["message"]
            if isinstance(msg, list):
              message = ", ".join(str(x) for x in msg)
            else:
              message = str(msg)
        except Exception:
          details = resp.text
      else:
        details = resp.text
      raise SellerApiError(resp.status_code, message, details=details, request_id=request_id)

    if is_json:
      return resp.json()
    return resp.text

  def upload_image(self, file_path: str) -> dict:
    """
    Upload a single image via Seller API key.

    Endpoint:
      POST /seller/v1/upload/image (multipart/form-data)

    Returns:
      { "url": "/uploads/images/..." }
    """
    path = os.fspath(file_path)
    url = _join_url(self.base_url, "/seller/v1/upload/image")
    filename = os.path.basename(path)
    mime, _ = mimetypes.guess_type(filename)
    with open(path, "rb") as f:
      files = {"file": (filename, f, mime or "application/octet-stream")}
      resp = self.session.post(url, files=files, timeout=self.timeout_s)  # type: ignore[union-attr]
    # Reuse error handling
    if not resp.ok:
      request_id = resp.headers.get("x-request-id") or resp.headers.get("x-requestid")
      try:
        details = resp.json()
      except Exception:
        details = resp.text
      message = resp.reason
      if isinstance(details, dict) and "message" in details:
        msg = details["message"]
        message = ", ".join(str(x) for x in msg) if isinstance(msg, list) else str(msg)
      raise SellerApiError(resp.status_code, message, details=details, request_id=request_id)
    return resp.json()

  def upload_images(self, file_paths: list[str]) -> dict:
    """
    Upload multiple images via Seller API key.

    Endpoint:
      POST /seller/v1/upload/images (multipart/form-data)

    Returns:
      { "urls": ["/uploads/images/...", ...] }
    """
    url = _join_url(self.base_url, "/seller/v1/upload/images")
    opened = []
    try:
      files = []
      for p in file_paths:
        path = os.fspath(p)
        filename = os.path.basename(path)
        mime, _ = mimetypes.guess_type(filename)
        f = open(path, "rb")
        opened.append(f)
        files.append(("files", (filename, f, mime or "application/octet-stream")))
      resp = self.session.post(url, files=files, timeout=self.timeout_s)  # type: ignore[union-attr]
      if not resp.ok:
        request_id = resp.headers.get("x-request-id") or resp.headers.get("x-requestid")
        try:
          details = resp.json()
        except Exception:
          details = resp.text
        message = resp.reason
        if isinstance(details, dict) and "message" in details:
          msg = details["message"]
          message = ", ".join(str(x) for x in msg) if isinstance(msg, list) else str(msg)
        raise SellerApiError(resp.status_code, message, details=details, request_id=request_id)
      return resp.json()
    finally:
      for f in opened:
        try:
          f.close()
        except Exception:
          pass

  def request_model(self, model: Any, method: str, path: str, json_body: Optional[dict] = None) -> Any:
    """
    Parse a successful JSON response into a pydantic model (requires `pip install solpay-seller[models]`).
    If pydantic is not installed, returns the raw JSON.
    """
    data = self.request(method, path, json_body=json_body)
    if not HAS_PYDANTIC:
      return data
    parsed = parse_model(model, data)
    return parsed if parsed is not None else data

  # ---- Seller API (public) ----

  # ---- Public helpers (no auth required, but safe with X-Api-Key header) ----

  def get_categories(self) -> list:
    """
    Fetch categories (public endpoint).

    Endpoint:
      GET /categories
    """
    return self.request("GET", "/categories")

  def me(self) -> dict:
    return self.request("GET", "/seller/v1/me")

  def me_model(self) -> Any:
    from .models import Me
    return self.request_model(Me, "GET", "/seller/v1/me")

  # Lots
  def list_lots(self, page: int = 1, limit: int = 20) -> LotsResponse:
    return self.request("GET", f"/seller/v1/lots?page={page}&limit={limit}")

  def list_lots_model(self, page: int = 1, limit: int = 20) -> Any:
    from .models import LotsResponse
    return self.request_model(LotsResponse, "GET", f"/seller/v1/lots?page={page}&limit={limit}")

  def create_lot(self, lot: dict) -> dict:
    return self.request("POST", "/seller/v1/lots", json_body=lot)

  def get_lot(self, lot_id: str) -> dict:
    return self.request("GET", f"/seller/v1/lots/{lot_id}")

  def update_lot(self, lot_id: str, patch: dict) -> dict:
    return self.request("PATCH", f"/seller/v1/lots/{lot_id}", json_body=patch)

  def delete_lot(self, lot_id: str) -> dict:
    return self.request("DELETE", f"/seller/v1/lots/{lot_id}")

  # Auto-delivery
  def get_auto_delivery_stats(self, lot_id: str) -> dict:
    return self.request("GET", f"/seller/v1/lots/{lot_id}/auto-delivery/stats")

  def import_auto_delivery_items(self, lot_id: str, text: str, delimiter: Optional[str] = None) -> dict:
    body: Dict[str, Any] = {"text": text}
    if delimiter is not None:
      body["delimiter"] = delimiter
    return self.request("POST", f"/seller/v1/lots/{lot_id}/auto-delivery/import", json_body=body)

  # Orders
  def list_orders(
    self,
    *,
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    kind: Optional[str] = None,
    from_iso: Optional[str] = None,
    to_iso: Optional[str] = None,
    lot_id: Optional[str] = None,
    buyer_id: Optional[str] = None,
  ) -> OrdersResponse:
    params = {
      "page": page,
      "limit": limit,
      "status": status,
      "kind": kind,
      "from": from_iso,
      "to": to_iso,
      "lotId": lot_id,
      "buyerId": buyer_id,
    }
    query = "&".join(f"{k}={requests.utils.quote(str(v))}" for k, v in params.items() if v is not None)
    return self.request("GET", f"/seller/v1/orders?{query}")

  def list_orders_model(self, **kwargs: Any) -> Any:
    from .models import OrdersResponse
    page = kwargs.pop("page", 1)
    limit = kwargs.pop("limit", 20)
    status = kwargs.pop("status", None)
    kind = kwargs.pop("kind", None)
    from_iso = kwargs.pop("from_iso", None)
    to_iso = kwargs.pop("to_iso", None)
    lot_id = kwargs.pop("lot_id", None)
    buyer_id = kwargs.pop("buyer_id", None)
    if kwargs:
      raise ValueError(f"Unknown args: {', '.join(kwargs.keys())}")

    params = {
      "page": page,
      "limit": limit,
      "status": status,
      "kind": kind,
      "from": from_iso,
      "to": to_iso,
      "lotId": lot_id,
      "buyerId": buyer_id,
    }
    query = "&".join(f"{k}={requests.utils.quote(str(v))}" for k, v in params.items() if v is not None)
    return self.request_model(OrdersResponse, "GET", f"/seller/v1/orders?{query}")

  def get_order(self, order_id: str) -> dict:
    return self.request("GET", f"/seller/v1/orders/{order_id}")

  def check_payment(self, order_id: str) -> dict:
    return self.request("POST", f"/seller/v1/orders/{order_id}/check-payment")

  def cancel_order(self, order_id: str) -> dict:
    return self.request("POST", f"/seller/v1/orders/{order_id}/cancel")

  def deliver_invoice(self, order_id: str) -> dict:
    return self.request("POST", f"/seller/v1/orders/{order_id}/deliver")

  # Messages
  def list_order_messages(self, order_id: str) -> list:
    return self.request("GET", f"/seller/v1/orders/{order_id}/messages")

  def send_order_message(self, order_id: str, content: str, attachments: Optional[list] = None) -> dict:
    body: Dict[str, Any] = {"content": content}
    if attachments is not None:
      body["attachments"] = attachments
    return self.request("POST", f"/seller/v1/orders/{order_id}/messages", json_body=body)

  # Service chats
  def list_service_chats(self, page: int = 1, limit: int = 20, include_closed: bool = False) -> dict:
    inc = "1" if include_closed else "0"
    return self.request("GET", f"/seller/v1/service-chats?page={page}&limit={limit}&includeClosed={inc}")

  def get_service_chat(self, chat_id: str) -> dict:
    return self.request("GET", f"/seller/v1/service-chats/{chat_id}")

  def create_service_invoice(self, chat_id: str, *, price_usd: int, title: Optional[str] = None, description: Optional[str] = None) -> dict:
    body: Dict[str, Any] = {"priceUsd": price_usd}
    if title is not None:
      body["title"] = title
    if description is not None:
      body["description"] = description
    return self.request("POST", f"/seller/v1/service-chats/{chat_id}/invoices", json_body=body)

  def close_service_chat(self, chat_id: str) -> dict:
    return self.request("POST", f"/seller/v1/service-chats/{chat_id}/close")

  # Webhooks
  def webhook_events(self) -> list:
    return self.request("GET", "/seller/v1/webhooks/events")

  def list_webhooks(self) -> list:
    return self.request("GET", "/seller/v1/webhooks")

  def create_webhook(self, *, url: str, events: Optional[list] = None, secret: Optional[str] = None) -> WebhookEndpoint:
    body: Dict[str, Any] = {"url": url}
    if events is not None:
      body["events"] = events
    if secret is not None:
      body["secret"] = secret
    return self.request("POST", "/seller/v1/webhooks", json_body=body)

  def update_webhook(self, webhook_id: str, *, url: Optional[str] = None, is_active: Optional[bool] = None, events: Optional[list] = None) -> WebhookEndpoint:
    body: Dict[str, Any] = {}
    if url is not None:
      body["url"] = url
    if is_active is not None:
      body["isActive"] = is_active
    if events is not None:
      body["events"] = events
    return self.request("PATCH", f"/seller/v1/webhooks/{webhook_id}", json_body=body)

  def delete_webhook(self, webhook_id: str) -> dict:
    return self.request("DELETE", f"/seller/v1/webhooks/{webhook_id}")
