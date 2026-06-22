import os
import time
import requests
from binance.client import Client

# ENV VARIABLES
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# SAFETY CHECK
if not TELEGRAM_TOKEN or not CHAT_ID:
    raise Exception("Telegram env missing")

client = Client(API_KEY, API_SECRET)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

# TELEGRAM FUNCTION
def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": text})
    except:
        print("Telegram error")

# PRICE FUNCTION
def get_price(symbol):
    try:
        return float(client.get_symbol_ticker(symbol=symbol)["price"])
    except:
        return None

# START MESSAGE
send_msg("🤖 Signal Bot STARTED")

# MAIN LOOP
while True:
    msg = "📊 Market Update:\n\n"

    for s in SYMBOLS:
        price = get_price(s)

        if price:
            msg += f"{s}: {price}\n"
        else:
            msg += f"{s}: error\n"

    send_msg(msg)

    time.sleep(60)
