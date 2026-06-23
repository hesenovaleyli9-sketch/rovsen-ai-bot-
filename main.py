import os
import time
import requests
from flask import Flask
from binance.client import Client

app = Flask(__name__)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

client = Client(API_KEY, API_SECRET)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

# =========================
# FUNCTIONS FIRST
# =========================

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": text})

def bot_loop():
    time.sleep(8)
    send_msg("🤖 Signal Bot STARTED")

    while True:
        msg = "📊 Market Update:\n\n"

        for s in SYMBOLS:
            try:
                price = client.get_symbol_ticker(symbol=s)["price"]
                msg += f"{s}: {price}\n"
            except:
                msg += f"{s}: error\n"

        send_msg(msg)
        time.sleep(60)

# =========================
# FLASK
# =========================

@app.route("/")
def home():
    return "Bot Running"

# =========================
# START THREAD LAST
# =========================

import threading
threading.Thread(target=bot_loop, daemon=True).start()

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
