import os
import time
import threading
import requests

from flask import Flask
from binance.client import Client


app = Flask(__name__)


# =========================
# ENV
# =========================

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


print("TOKEN CHECK:", TELEGRAM_TOKEN[:10] if TELEGRAM_TOKEN else "NO TOKEN")
print("CHAT CHECK:", CHAT_ID)


# =========================
# BINANCE
# =========================

client = Client(API_KEY, API_SECRET)

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT"
]


# =========================
# TELEGRAM
# =========================

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        r = requests.get(
            url,
            params={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=10
        )

        print("TELEGRAM STATUS:", r.status_code)
        print("TELEGRAM RESPONSE:", r.text)

    except Exception as e:
        print("TELEGRAM ERROR:", e)



# =========================
# BOT LOOP
# =========================

def bot_loop():

    print("BOT LOOP STARTED")

    time.sleep(5)

    send_msg("🔥 BOT SUCCESSFULLY STARTED")

    while True:

        message = "📊 MARKET UPDATE\n\n"

        for symbol in SYMBOLS:

            try:

                price = client.get_symbol_ticker(
                    symbol=symbol
                )["price"]

                message += f"{symbol}: {price}\n"

            except Exception as e:

                print("BINANCE ERROR:", e)

                message += f"{symbol}: ERROR\n"


        send_msg(message)

        time.sleep(60)



# =========================
# FLASK
# =========================

@app.route("/")
def home():

    return "Bot Running"



# =========================
# START
# =========================

threading.Thread(
    target=bot_loop,
    daemon=True
).start()



if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
