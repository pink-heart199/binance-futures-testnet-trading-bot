from typing import Any, Dict, Optional

from .client import BinanceClient, BinanceClientError
from .logging_config import setup_logger

logger = setup_logger("trading_bot.orders")


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Place a market or limit order via the supplied Binance client.

    Returns the raw API response dict on success.
    Raises BinanceClientError on API failure.
    """
    logger.info(
        "Placing %s %s order | symbol=%s | qty=%s | price=%s",
        side,
        order_type,
        symbol,
        quantity,
        price if price is not None else "N/A (MARKET)",
    )

    response = client.place_order(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
    )

    logger.info(
        "Order placed successfully | orderId=%s | status=%s | executedQty=%s | avgPrice=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
        response.get("avgPrice", "N/A"),
    )

    return response


def format_order_summary(params: Dict[str, Any]) -> str:
    """Return a human-readable summary of the order request."""
    lines = [
        "=" * 50,
        "  ORDER REQUEST SUMMARY",
        "=" * 50,
        f"  Symbol     : {params['symbol']}",
        f"  Side       : {params['side']}",
        f"  Type       : {params['order_type']}",
        f"  Quantity   : {params['quantity']}",
    ]
    if params.get("price") is not None:
        lines.append(f"  Price      : {params['price']}")
    lines.append("=" * 50)
    return "\n".join(lines)


def format_order_response(response: Dict[str, Any]) -> str:
    """Return a human-readable summary of the API order response."""
    lines = [
        "=" * 50,
        "  ORDER RESPONSE",
        "=" * 50,
        f"  Order ID   : {response.get('orderId', 'N/A')}",
        f"  Symbol     : {response.get('symbol', 'N/A')}",
        f"  Side       : {response.get('side', 'N/A')}",
        f"  Type       : {response.get('type', 'N/A')}",
        f"  Status     : {response.get('status', 'N/A')}",
        f"  Qty (req)  : {response.get('origQty', 'N/A')}",
        f"  Qty (exec) : {response.get('executedQty', 'N/A')}",
        f"  Avg Price  : {response.get('avgPrice', 'N/A')}",
        f"  Time       : {response.get('updateTime', 'N/A')}",
        "=" * 50,
    ]
    return "\n".join(lines)
