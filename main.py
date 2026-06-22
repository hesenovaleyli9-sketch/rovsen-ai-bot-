import os
import time
import requests
from binance.client import Client

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

client = Client(API_KEY, API_SECRET)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": text})

def get_price(symbol):
    return float(client.get_symbol_ticker(symbol=symbol)["price"])

send_msg("🤖 Bot STARTED")

while True:
    msg = "Market update:\n\n"

    for s in SYMBOLS:
        price = get_price(s)
        msg += f"{s}: {price}\n"

    send_msg(msg)

    time.sleep(60)
