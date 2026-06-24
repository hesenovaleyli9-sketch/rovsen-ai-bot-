import os
import time
import threading
import pandas as pd

from flask import Flask
from binance.client import Client
from telegram import Bot
import ta


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
        print("Telegram error:", e)



def analyze(symbol):

    try:

        candles = client.get_klines(
            symbol=symbol,
            interval="1h",
            limit=100
        )


        df = pd.DataFrame(
            candles,
            columns=[
                "time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "x1",
                "x2",
                "x3",
                "x4",
                "x5",
                "x6"
            ]
        )


        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)


        price = df["close"].iloc[-1]


        rsi = ta.momentum.RSIIndicator(
            df["close"]
        ).rsi().iloc[-1]


        volume = df["volume"].iloc[-1]

        score = 0


        if rsi > 55:
            score += 3

        if volume > df["volume"].mean():
            score += 3


        if price > df["close"].rolling(20).mean().iloc[-1]:
            score += 2


        return price, rsi, volume, score


    except:

        return None





def market_scan():


    while True:


        try:


            exchange = client.get_exchange_info()


            symbols = []


            for x in exchange["symbols"]:

                if (
                    x["quoteAsset"] == "USDT"
                    and x["status"] == "TRADING"
                ):
                    symbols.append(
                        x["symbol"]
                    )



            opportunities = []


            for s in symbols[:300]:


                result = analyze(s)


                if result:


                    price,rsi,vol,score = result


                    if score >= 7:


                        opportunities.append(

                            (
                            score,
                            s,
                            price,
                            rsi
                            )

                        )



            opportunities.sort(
                reverse=True
            )



            msg = "🧠 AI CRYPTO ANALYST V3.1\n\n"



            if opportunities:


                for x in opportunities[:10]:


                    msg += (
                        f"🚀 {x[1]}\n"
                        f"Qiymət: {x[2]}\n"
                        f"RSI: {round(x[3],2)}\n"
                        f"Score: {x[0]}/8\n"
                        f"Status: İzləmə / Fürsət\n\n"
                    )


            else:


                msg += (
                    "👀 Hazırda güclü fürsət yoxdur\n"
                    "Bazar izlənilir..."
                )



            send(msg)



        except Exception as e:

            print(e)



        time.sleep(1800)





@app.route("/")
def home():

    return "AI BOT AKTIV"



def start():

    thread = threading.Thread(
        target=market_scan
    )

    thread.start()



if __name__ == "__main__":


    print("BOT STARTED")


    start()


    app.run(
        host="0.0.0.0",
        port=10000
    )
