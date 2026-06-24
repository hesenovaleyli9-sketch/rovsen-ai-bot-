import os
import time
import threading
from flask import Flask
from binance.client import Client
import ta

from telegram import Bot

app = Flask(__name__)

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

client = Client()


def send(text):
    try:
        bot.send_message(
            chat_id=CHAT_ID,
            text=text
        )
    except Exception as e:
        print(e)


def market_scan():

    while True:

        try:

            symbols = [
                "BTCUSDT",
                "ETHUSDT",
                "SOLUSDT",
                "XRPUSDT",
                "DOGEUSDT",
                "SUIUSDT",
                "INJUSDT",
                "LINKUSDT",
                "AVAXUSDT"
            ]


            msg = "🧠 AI CRYPTO ANALYST V3\n\n"


            for s in symbols:

                candles = client.get_klines(
                    symbol=s,
                    interval="1h",
                    limit=100
                )


                closes = [
                    float(x[4])
                    for x in candles
                ]


                rsi = ta.momentum.RSIIndicator(
                    close=__import__("pandas").Series(closes)
                ).rsi().iloc[-1]


                price = closes[-1]


                if rsi > 55:

                    msg += (
                        f"🚀 {s}\n"
                        f"Qiymət: {price}\n"
                        f"RSI: {round(rsi,2)}\n"
                        f"Status: Güclü trend\n\n"
                    )


            if msg != "🧠 AI CRYPTO ANALYST V3\n\n":

                send(msg)

            else:

                send(
                    "👀 Hazırda güclü fürsət yoxdur\n"
                    "Bazar izlənilir..."
                )


        except Exception as e:

            print(e)


        time.sleep(1800)



@app.route("/")
def home():

    return "AI BOT AKTIV"



def start():

    t = threading.Thread(
        target=market_scan
    )

    t.start()


if __name__ == "__main__":

    print("BOT STARTED")

    start()

    app.run(
        host="0.0.0.0",
        port=10000
    )
