from .client import SellerApiClient
from .exceptions import SellerApiError
from .compat import HAS_PYDANTIC

if HAS_PYDANTIC:
  from .models import Me, Lot, LotsResponse, Order, OrdersResponse, WebhookEndpoint  # noqa: F401

try:
  from importlib.metadata import version as _pkg_version

  __version__ = _pkg_version("solpay-seller")
except Exception:  # pragma: no cover
  __version__ = "0.0.0"

__all__ = ["SellerApiClient", "SellerApiError", "HAS_PYDANTIC", "__version__"]
