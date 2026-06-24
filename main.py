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


print("TOKEN:", TELEGRAM_TOKEN[:10] if TELEGRAM_TOKEN else "NO TOKEN")
print("CHAT:", CHAT_ID)


client = Client(API_KEY, API_SECRET)


SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT"
]


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

        print("ERROR:", e)



def bot_loop():

    time.sleep(5)

    print("BOT LOOP STARTED")

    send_msg("🤖 Signal Bot STARTED")


    while True:

        msg = "📊 Market Update\n\n"


        for s in SYMBOLS:

            try:

                price = client.get_symbol_ticker(symbol=s)["price"]

                msg += f"{s}: {price}\n"


            except Exception as e:

                print("BINANCE ERROR:", e)

                msg += f"{s}: ERROR\n"



        send_msg(msg)

        time.sleep(60)



@app.route("/")
def home():

    return "Bot Running"



if __name__ == "__main__":


    threading.Thread(
        target=bot_loop,
        daemon=True
    ).start()


    port = int(os.environ.get("PORT",10000))


    app.run(
        host="0.0.0.0",
        port=port
    )
