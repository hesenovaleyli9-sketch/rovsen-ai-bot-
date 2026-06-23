import os
import time
import requests
import threading
from flask import Flask
from binance.client import Client

app = Flask(__name__)

# =========================
# ENV VARIABLES
# =========================
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# =========================
# BINANCE CLIENT
# =========================
client = Client(API_KEY, API_SECRET)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

# =========================
# TELEGRAM FUNCTION
# =========================
def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={
            "chat_id": CHAT_ID,
            "text": text
        })
    except Exception as e:
        print("Telegram error:", e)

# =========================
# BOT LOOP
# =========================
def bot_loop():
    time.sleep(5)

    print("BOT LOOP STARTED")

    # TEST MESSAGE
    send_msg("🔥 BOT SUCCESSFULLY STARTED ON RENDER")

    while True:
        msg = "📊 MARKET UPDATE:\n\n"

        for symbol in SYMBOLS:
            try:
                price = client.get_symbol_ticker(symbol=symbol)["price"]
                msg += f"{symbol}: {price}\n"
            except Exception:
                msg += f"{symbol}: error\n"

        send_msg(msg)
        time.sleep(60)

# =========================
# FLASK ROUTE
# =========================
@app.route("/")
def home():
    return "Bot is running"

# =========================
# START BOT THREAD
# =========================
threading.Thread(target=bot_loop, daemon=True).start()

# =========================
# RUN SERVER (RENDER FIX)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
