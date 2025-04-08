import requests
import json
import datetime

# 🔐 Replace with your actual credentials
CLIENT_ID = "1100147239"
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzQ2NjA2NDM1LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDE0NzIzOSJ9.fn9Ke_uC8KAhB8Tp8fiaNu7G3nm86zteM_j-5syHez_6ax6_hDs7BULB0YKxbBGgKG1oOqQrFDARAxfv3DaI8g"
DEFAULT_PRODUCT_TYPE = "INTRADAY"
DEFAULT_ORDER_TYPE = "MARKET"
EXCHANGE = "NSE"
TRADE_SYMBOL = "NIFTY"

# 🛣️ API base
BASE_URL = "https://api.dhan.co"

# 🔧 Headers for all API calls
HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID
}

# 📦 Fetch ATM Option Symbol
def get_atm_option_symbol(option_type):
    # Step 1: Get NIFTY spot price
    spot_data = requests.get(f"{BASE_URL}/quotes/indices/{TRADE_SYMBOL}", headers=HEADERS).json()
    spot_price = spot_data.get("last_traded_price", 0)

    # Step 2: Round to nearest 50
    strike = int(round(spot_price / 50.0) * 50)

    # Step 3: Generate symbol
    expiry = get_current_weekly_expiry()
    option_symbol = f"{TRADE_SYMBOL}{expiry}{strike}{option_type}"
    return option_symbol

# 📅 Get current weekly expiry date in Dhan format
def get_current_weekly_expiry():
    today = datetime.date.today()
    weekday = today.weekday()
    days_ahead = 3 - weekday if weekday <= 3 else 10 - weekday  # Thursday expiry
    expiry = today + datetime.timedelta(days=days_ahead)
    return expiry.strftime("%y%b").upper() + str(expiry.day).zfill(2)

# 🛒 Place Order
def place_order(symbol, side, quantity=75):
    payload = {
        "transaction_type": "BUY" if side == "BUY" else "SELL",
        "exchange_segment": "NSE_OPTION",
        "product_type": DEFAULT_PRODUCT_TYPE,
        "order_type": DEFAULT_ORDER_TYPE,
        "validity": "DAY",
        "security_id": symbol,
        "quantity": quantity,
        "disclosed_quantity": 0,
        "price": 0,
        "trigger_price": 0,
        "after_market_order": False
    }
    response = requests.post(f"{BASE_URL}/orders", headers=HEADERS, data=json.dumps(payload))
    return response.json()

# ❌ Exit All Open Positions
def exit_all_positions():
    positions = requests.get(f"{BASE_URL}/positions", headers=HEADERS).json()
    for pos in positions:
        if pos["product_type"] == DEFAULT_PRODUCT_TYPE and pos["exchange_segment"] == "NSE_OPTION":
            side = "SELL" if pos["buy_quantity"] > pos["sell_quantity"] else "BUY"
            symbol = pos["security_id"]
            place_order(symbol, side, quantity=pos["net_quantity"])

