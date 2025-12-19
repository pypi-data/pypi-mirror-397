from __future__ import annotations

import hmac
import hashlib


def compute_signature(raw_body: bytes, secret: str) -> str:
  digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
  return f"sha256={digest}"


def verify_signature(raw_body: bytes, signature_header: str, secret: str) -> bool:
  if not signature_header or not signature_header.startswith("sha256="):
    return False
  expected = compute_signature(raw_body, secret)
  return hmac.compare_digest(expected, signature_header)

