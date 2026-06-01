#!/usr/bin/env python3
"""
cli.py — CLI entry point for the Binance Futures Testnet trading bot.

Usage examples:
  # Market BUY
  python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET \
      --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # Limit SELL
  python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET \
      --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000

  # Using environment variables (recommended)
  export BINANCE_API_KEY=your_key
  export BINANCE_API_SECRET=your_secret
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
"""

import argparse
import os
import sys

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.orders import format_order_response, format_order_summary, place_order
from bot.validators import ValidationError, validate_all

logger = setup_logger("trading_bot.cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place Market or Limit orders on Binance Futures Testnet (USDT-M).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Credentials — can also come from env vars
    parser.add_argument(
        "--api-key",
        default=os.environ.get("BINANCE_API_KEY"),
        help="Binance Testnet API key (or set BINANCE_API_KEY env var).",
    )
    parser.add_argument(
        "--api-secret",
        default=os.environ.get("BINANCE_API_SECRET"),
        help="Binance Testnet API secret (or set BINANCE_API_SECRET env var).",
    )

    # Order parameters
    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading pair symbol, e.g. BTCUSDT.",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        type=str.upper,
        help="Order side: BUY or SELL.",
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT"],
        type=str.upper,
        help="Order type: MARKET or LIMIT.",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        help="Order quantity (e.g. 0.001 for BTC).",
    )
    parser.add_argument(
        "--price",
        default=None,
        help="Limit price — required for LIMIT orders, ignored for MARKET.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # --- Validate credentials ---
    if not args.api_key:
        parser.error(
            "API key is required. Pass --api-key or set the BINANCE_API_KEY environment variable."
        )
    if not args.api_secret:
        parser.error(
            "API secret is required. Pass --api-secret or set the BINANCE_API_SECRET environment variable."
        )

    # --- Validate order parameters ---
    try:
        params = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValidationError as exc:
        logger.error("Input validation failed: %s", exc)
        print(f"\n[ERROR] Validation failed: {exc}\n")
        sys.exit(1)

    # --- Print request summary ---
    print(format_order_summary(params))
    logger.info("Order request: %s", params)

    # --- Build client and place order ---
    try:
        client = BinanceClient(api_key=args.api_key, api_secret=args.api_secret)
        response = place_order(
            client=client,
            symbol=params["symbol"],
            side=params["side"],
            order_type=params["order_type"],
            quantity=params["quantity"],
            price=params["price"],
        )
    except BinanceClientError as exc:
        logger.error("Order placement failed: %s", exc)
        print(f"\n[FAILED] Order could not be placed.\nReason: {exc}\n")
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error: %s", exc)
        print(f"\n[ERROR] An unexpected error occurred: {exc}\n")
        sys.exit(1)

    # --- Print response ---
    print(format_order_response(response))
    print("\n[SUCCESS] Order placed successfully.\n")


if __name__ == "__main__":
    main()
