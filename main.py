import os
import time
import threading
import requests
from flask import Flask
from binance.client import Client

app = Flask(__name__)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise Exception("Telegram env missing")

client = Client(API_KEY, API_SECRET)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]


def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.get(url, params={
        "chat_id": CHAT_ID,
        "text": text
    })


def bot():
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


@app.route("/")
def home():
    return "Signal Bot Running"


threading.Thread(target=bot).start()


port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
