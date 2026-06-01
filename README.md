# Binance Futures Testnet Trading Bot

A Python CLI application that places **Market** and **Limit** orders on the **Binance Futures Testnet (USDT-M)**.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API client wrapper
│   ├── orders.py          # Order placement logic & output formatting
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Logging setup (file + console)
├── cli.py                 # CLI entry point (argparse)
├── logs/                  # Auto-created; log files written here
├── README.md
└── requirements.txt
```

---

## Setup

### 1. Binance Futures Testnet Account

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com) and register / log in.
2. Navigate to **API Management** and generate a new API key + secret.
3. Keep both values — you will need them below.

### 2. Python Environment

```bash
# Clone or unzip the project, then:
cd trading_bot

# (Optional but recommended) create a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Credentials

You can supply credentials in two ways (env vars are recommended):

**Option A — environment variables (recommended)**
```bash
export BINANCE_API_KEY=your_testnet_api_key
export BINANCE_API_SECRET=your_testnet_api_secret
```

**Option B — CLI flags**
```bash
python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET ...
```

---

## How to Run

### Place a Market BUY order

```bash
python cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.001
```

### Place a Market SELL order

```bash
python cli.py \
  --symbol ETHUSDT \
  --side SELL \
  --type MARKET \
  --quantity 0.01
```

### Place a Limit BUY order

```bash
python cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --type LIMIT \
  --quantity 0.001 \
  --price 95000
```

### Place a Limit SELL order

```bash
python cli.py \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.001 \
  --price 105000
```

### Help

```bash
python cli.py --help
```

---

## Example Output

```
==================================================
  ORDER REQUEST SUMMARY
==================================================
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
==================================================
==================================================
  ORDER RESPONSE
==================================================
  Order ID   : 4389271048
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Status     : FILLED
  Qty (req)  : 0.001
  Qty (exec) : 0.001
  Avg Price  : 103241.50
  Time       : 1747742462456
==================================================

[SUCCESS] Order placed successfully.
```

---

## Logging

Logs are written automatically to `logs/trading_bot_YYYYMMDD.log`.

- **Console** — INFO level and above (order summaries, success/error messages).
- **Log file** — DEBUG level and above (full API request params, raw responses, errors).

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing / invalid symbol, side, type, quantity, price | Validation error printed; exits with code 1 |
| Missing price on a LIMIT order | Validation error; exits with code 1 |
| Network / connection failure | Error logged and printed; exits with code 1 |
| Binance API error (e.g. invalid quantity, insufficient margin) | Error code + message printed; exits with code 1 |
| Missing API credentials | Argument parser error; usage printed |

---

## Assumptions

- All orders are placed under **One-Way position mode** (`positionSide=BOTH` default).
- LIMIT orders use `timeInForce=GTC` (Good Till Cancelled).
- The `price` flag is silently ignored for MARKET orders.
- Quantity precision must satisfy the symbol's LOT_SIZE filter on the testnet. Use at least 3 decimal places for BTC (e.g. `0.001`) and 2 for ETH (e.g. `0.01`).
- Credentials are read from CLI flags or environment variables; they are never hard-coded.

---

## Dependencies

| Package | Version |
|---|---|
| requests | >=2.31.0 |

Only the Python standard library and `requests` are used — no Binance SDK required.
