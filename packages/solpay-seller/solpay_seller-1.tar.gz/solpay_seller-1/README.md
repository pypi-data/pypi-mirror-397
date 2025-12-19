# solpay-seller — Python SDK for Seller API

`solpay-seller` is a batteries-included Python client for the **public Seller API** (auth via `X-Api-Key: sp_sk_...`) used to:
- create/update lots (products & services)
- manage auto-delivery stock for product lots
- read sales orders
- send messages to buyers (order chat)
- manage webhooks (receive events like `order.paid`, `message.created`)
- upload images for lots (multipart)

If you only read this README on PyPI, you should be able to write a full bot:
**create lot → wait for purchase webhook → send random 1..100 → reply ping/pong**.

---

## Installation

```bash
pip install solpay-seller
```

Optional extras:

```bash
# Pydantic models for typed parsing (optional)
pip install "solpay-seller[models]"

# Docs toolchain (mkdocs) (optional)
pip install "solpay-seller[docs]"
```

---

## Getting an API key

Create a Seller API key in the dashboard:
- **Dashboard → Integrations → API Keys**

Key format:
- `sp_sk_...` (secret, shown only once)

You must send it as:
- `X-Api-Key: sp_sk_...`

---

## Quickstart

```py
from solpay_seller import SellerApiClient

client = SellerApiClient(
  api_key="sp_sk_...",
  base_url="https://solpay.one/api",  # IMPORTANT: include /api
)

print(client.me())  # { "id": "..." }
print(client.list_lots(page=1, limit=20)["total"])
```

---

## Creating a lot (and finding `categoryId`)

To create a lot you need a valid `categoryId`. Categories are public:

```py
cats = client.get_categories()
print(cats[0]["id"], cats[0]["name"])
category_id = cats[0]["id"]
```

Create a product lot (prices are in **cents**):

```py
lot = client.create_lot({
  "type": "PRODUCT",
  "title": "Steam key",
  "description": "<p>Instant delivery</p>",
  "priceUsd": 499,
  "categoryId": category_id,
  "quantity": 0,              # ignored if autoDeliveryEnabled=true
  "acceptToken": False,
  "images": [],
  "tags": ["steam", "key"],
  "isActive": True,

  # Optional: automatic first message after payment
  "autoFirstMessageEnabled": True,
  "autoFirstMessageText": "Thanks! If you need help, reply here. (ping -> pong)",

  # Optional: auto-delivery settings (unique items pool)
  "autoDeliveryEnabled": True,
  "autoDeliveryEmptyAction": "BLOCK_PURCHASE",  # or "ALLOW_MANUAL"
  "autoDeliveryDelimiter": "\\n",
  "autoDeliveryNotifyOnEmpty": True,
})

lot_id = lot["id"]
print("lot_id:", lot_id)
```

---

## Uploading images (for lots)

If you want lot images, upload first, then pass returned URLs in `images`.

```py
uploaded = client.upload_image("./image.png")
image_url = uploaded["url"]  # "/uploads/images/....png"

lot = client.create_lot({
  "type": "PRODUCT",
  "title": "With image",
  "description": "<p>...</p>",
  "priceUsd": 199,
  "categoryId": category_id,
  "quantity": 0,
  "acceptToken": False,
  "images": [image_url],
  "tags": [],
  "isActive": True,
})
```

Multiple images:

```py
res = client.upload_images(["./a.png", "./b.png"])
urls = res["urls"]
```

---

## Auto-delivery stock (import items)

Auto-delivery stock is a pool of unique items. Each paid order consumes `N` items where `N = order.quantity`.

Import “one item per line” using delimiter `\\n`:

```py
client.import_auto_delivery_items(
  lot_id,
  text="KEY1\nKEY2\nKEY3",
  delimiter="\\n",
)
print(client.get_auto_delivery_stats(lot_id))
```

Multi-line items are supported via a custom delimiter:

```py
client.import_auto_delivery_items(
  lot_id,
  delimiter="---",
  text="USER:pass\nnote line 2---USER2:pass2\nnote2",
)
```

---

## Edit / update a lot

```py
updated = client.update_lot(lot_id, {"priceUsd": 599, "title": "Steam key (v2)"})
print(updated["priceUsd"], updated["title"])
```

---

## Webhooks: receive purchases + messages (ping → pong)

You should use webhooks to “wait” for events:
- `order.paid` when an order is paid
- `message.created` when a message appears in an order chat

### 1) Register a webhook endpoint

```py
webhook = client.create_webhook(
  url="https://YOUR_PUBLIC_DOMAIN/webhooks/solpay",
  events=["order.paid", "message.created"],
  secret="your-webhook-secret",
)
print("webhook_id:", webhook["id"])
```

### 2) Receive and verify webhooks (Flask example)

Install:
```bash
pip install flask
```

Run this file as a bot:

```py
import json
import random
import threading
from flask import Flask, request, abort

from solpay_seller import SellerApiClient
from solpay_seller.webhooks import verify_signature

API_KEY = "sp_sk_..."
BASE_URL = "https://solpay.one/api"
WEBHOOK_SECRET = "your-webhook-secret"

client = SellerApiClient(api_key=API_KEY, base_url=BASE_URL)

state = {
  "seller_id": None,
  "lot_id": None,
}

app = Flask(__name__)

@app.post("/webhooks/solpay")
def hook():
  raw = request.get_data(cache=False)
  sig = request.headers.get("X-SolPay-Signature", "")
  if not verify_signature(raw_body=raw, signature_header=sig, secret=WEBHOOK_SECRET):
    abort(401, "bad signature")

  payload = json.loads(raw.decode("utf-8"))
  event = (payload.get("type") or "").lower()
  data = payload.get("data") or {}

  # A) On purchase of OUR lot -> send random 1..100
  if event == "order.paid":
    order_id = data.get("id")
    lot = data.get("lot") or {}
    if order_id and lot.get("id") == state["lot_id"]:
      client.send_order_message(order_id, f"Your random number: {random.randint(1, 100)}")

  # B) If someone wrote "ping" -> reply "pong"
  if event == "message.created":
    order_id = data.get("orderId")
    msg = (data.get("message") or {})
    sender_id = msg.get("senderId")
    content = (msg.get("content") or "").strip().lower()

    # ignore our own messages
    if order_id and content == "ping" and sender_id and sender_id != state["seller_id"]:
      client.send_order_message(order_id, "pong")

  return {"ok": True}

def bootstrap():
  # Identify ourselves (used to ignore own messages)
  me = client.me()
  state["seller_id"] = me["id"]

  # Create lot (you need a real categoryId)
  category_id = client.get_categories()[0]["id"]

  # Optional: upload an image and attach it to the lot
  image_url = None
  try:
    uploaded = client.upload_image("./image.png")
    image_url = uploaded.get("url")
    if image_url:
      print("Uploaded image:", image_url)
  except Exception as e:
    print("Image upload skipped:", e)

  lot = client.create_lot({
    "type": "PRODUCT",
    "title": "Demo lot (python bot)",
    "description": "<p>Auto delivery + ping/pong demo</p>",
    "priceUsd": 199,
    "categoryId": category_id,
    "quantity": 0,
    "acceptToken": False,
    "images": [image_url] if image_url else [],
    "tags": ["demo"],
    "isActive": True,
    "autoDeliveryEnabled": True,
    "autoDeliveryEmptyAction": "BLOCK_PURCHASE",
    "autoDeliveryDelimiter": "\\n",
    "autoDeliveryNotifyOnEmpty": True,
  })

  state["lot_id"] = lot["id"]

  # Add auto-delivery items
  client.import_auto_delivery_items(state["lot_id"], "ITEM1\nITEM2\nITEM3", delimiter="\\n")

  # Edit lot
  client.update_lot(state["lot_id"], {"title": "Demo lot (python bot) v2", "priceUsd": 249})

  # Register webhook endpoint (use your real public URL)
  client.create_webhook(
    url="https://YOUR_PUBLIC_DOMAIN/webhooks/solpay",
    events=["order.paid", "message.created"],
    secret=WEBHOOK_SECRET,
  )

  print("Ready. Waiting for webhooks...")

if __name__ == "__main__":
  # Tip: for local testing use ngrok:
  #   ngrok http 8000
  threading.Thread(target=bootstrap, daemon=True).start()
  app.run(host="0.0.0.0", port=8000)
```

---

## Orders & messages (manual polling)

Webhooks are best, but you can also poll:

```py
orders = client.list_orders(page=1, limit=20, status="PAID")["orders"]
for o in orders:
  print(o["id"], o["status"])

msgs = client.list_order_messages(order_id="ord_...")
print(msgs[-1]["content"])
```

Send a message:

```py
client.send_order_message("ord_...", "Hello! Thanks for your purchase.")
```

---

## Service chats (SERVICE lots)

```py
chats = client.list_service_chats(page=1, limit=20, include_closed=False)
chat_id = chats["orders"][0]["id"]

invoice = client.create_service_invoice(chat_id, price_usd=2500, title="Stage 1")
client.close_service_chat(chat_id)
```

---

## Pydantic models (optional)

If installed (`pip install "solpay-seller[models]"`) you can use:

- `me_model()`
- `list_lots_model()`
- `list_orders_model()`

They return pydantic objects; otherwise they fall back to raw JSON `dict`.

---

## Error handling

All non-2xx responses raise `SellerApiError`:

```py
from solpay_seller import SellerApiClient, SellerApiError

client = SellerApiClient(api_key="sp_sk_...", base_url="https://solpay.one/api")

try:
  client.get_lot("missing_id")
except SellerApiError as e:
  print("status:", e.status_code)
  print("message:", e.message)
  print("details:", e.details)
```

---

## Full API reference (all client methods)

### Public helpers
- `get_categories() -> list`

### Auth / identity
- `me() -> dict`
- `me_model() -> pydantic model | dict`

### Uploads
- `upload_image(file_path: str) -> dict` → `{ "url": "/uploads/images/..." }`
- `upload_images(file_paths: list[str]) -> dict` → `{ "urls": [...] }`

### Lots
- `list_lots(page=1, limit=20) -> dict`
- `list_lots_model(page=1, limit=20) -> pydantic model | dict`
- `create_lot(lot: dict) -> dict`
- `get_lot(lot_id: str) -> dict`
- `update_lot(lot_id: str, patch: dict) -> dict`
- `delete_lot(lot_id: str) -> dict`

### Auto-delivery
- `get_auto_delivery_stats(lot_id: str) -> dict`
- `import_auto_delivery_items(lot_id: str, text: str, delimiter: str | None = None) -> dict`

### Orders
- `list_orders(page=1, limit=20, status=None, kind=None, from_iso=None, to_iso=None, lot_id=None, buyer_id=None) -> dict`
- `list_orders_model(...) -> pydantic model | dict`
- `get_order(order_id: str) -> dict`
- `check_payment(order_id: str) -> dict`
- `cancel_order(order_id: str) -> dict`
- `deliver_invoice(order_id: str) -> dict` (service invoices only)

### Messages
- `list_order_messages(order_id: str) -> list`
- `send_order_message(order_id: str, content: str, attachments: list | None = None) -> dict`

### Service chats
- `list_service_chats(page=1, limit=20, include_closed=False) -> dict`
- `get_service_chat(chat_id: str) -> dict`
- `create_service_invoice(chat_id: str, price_usd: int, title: str|None=None, description: str|None=None) -> dict`
- `close_service_chat(chat_id: str) -> dict`

### Webhooks
- `webhook_events() -> list`
- `list_webhooks() -> list`
- `create_webhook(url: str, events: list|None=None, secret: str|None=None) -> dict`
- `update_webhook(webhook_id: str, url: str|None=None, is_active: bool|None=None, events: list|None=None) -> dict`
- `delete_webhook(webhook_id: str) -> dict`

### Low-level
- `request(method: str, path: str, json_body: dict | None = None) -> dict | str`

---
