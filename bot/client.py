import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from .logging_config import setup_logger

BASE_URL = "https://testnet.binancefuture.com"

logger = setup_logger("trading_bot.client")


class BinanceClientError(Exception):
    """Raised for Binance API-level errors (non-2xx or error payload)."""
    pass


class BinanceClient:
    """Thin wrapper around the Binance Futures Testnet REST API."""

    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must not be empty.")
        self._api_key = api_key
        self._api_secret = api_secret
        self._session = requests.Session()
        self._session.headers.update({
            "X-MBX-APIKEY": self._api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Append a HMAC-SHA256 signature to the params dict."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self._api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        """Execute an HTTP request and return the parsed JSON response."""
        url = f"{BASE_URL}{endpoint}"
        params = params or {}

        if signed:
            params = self._sign(params)

        logger.debug("REQUEST  %s %s | params=%s", method.upper(), endpoint, {k: v for k, v in params.items() if k != "signature"})

        try:
            response = self._session.request(method, url, params=params, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error while calling %s: %s", endpoint, exc)
            raise BinanceClientError(f"Network connection error: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            logger.error("Request to %s timed out: %s", endpoint, exc)
            raise BinanceClientError(f"Request timed out: {exc}") from exc

        logger.debug("RESPONSE %s %s | status=%s | body=%s", method.upper(), endpoint, response.status_code, response.text[:500])

        try:
            data = response.json()
        except ValueError:
            logger.error("Non-JSON response from %s (status %s): %s", endpoint, response.status_code, response.text[:200])
            raise BinanceClientError(f"Unexpected non-JSON response (HTTP {response.status_code}).")

        if not response.ok or (isinstance(data, dict) and "code" in data and data["code"] != 200):
            code = data.get("code", response.status_code)
            msg = data.get("msg", response.text)
            logger.error("API error from %s | code=%s | msg=%s", endpoint, code, msg)
            raise BinanceClientError(f"Binance API error [{code}]: {msg}")

        return data

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def get_exchange_info(self) -> Dict[str, Any]:
        """Fetch exchange info (symbol list, filters, etc.)."""
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: str = "GTC",
    ) -> Dict[str, Any]:
        """
        Place a futures order.

        Parameters
        ----------
        symbol       : e.g. "BTCUSDT"
        side         : "BUY" or "SELL"
        order_type   : "MARKET" or "LIMIT"
        quantity     : order quantity
        price        : required for LIMIT orders
        time_in_force: "GTC" (default) for LIMIT orders
        """
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            if price is None:
                raise BinanceClientError("Price must be provided for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = time_in_force

        return self._request("POST", "/fapi/v1/order", params=params, signed=True)
