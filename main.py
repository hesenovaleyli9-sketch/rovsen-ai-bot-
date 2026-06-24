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


        df = pd.DataFrame(candles)

        df["close"] = df[4].astype(float)
        df["volume"] = df[5].astype(float)


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


    except Exception as e:

        print(symbol,e)

        return None




def market_scan():


    while True:


        try:


            info = client.get_exchange_info()


            symbols=[]


            for x in info["symbols"]:


                if (
                    x["quoteAsset"]=="USDT"
                    and x["status"]=="TRADING"
                ):

                    symbols.append(
                        x["symbol"]
                    )



            results=[]


            for s in symbols[:500]:


                data=analyze(s)


                if data:


                    price,rsi,vol,score=data


                    if score>=7:


                        results.append(
                            (
                                score,
                                s,
                                price,
                                rsi
                            )
                        )



            results.sort(
                reverse=True
            )


            msg="🧠 AI CRYPTO ANALYST V4\n\n"



            if results:


                for r in results[:15]:


                    msg += (
                    f"🚀 {r[1]}\n"
                    f"💰 Qiymət: {round(r[2],6)}\n"
                    f"📊 RSI: {round(r[3],2)}\n"
                    f"⭐ Score: {r[0]}/8\n"
                    f"👀 Nəzarət / Fürsət\n\n"
                    )


            else:


                msg += (
                "⏳ Güclü fürsət tapılmadı\n"
                "Bazar skan edilir..."
                )


            send(msg)



        except Exception as e:

            print("SCAN ERROR",e)



        time.sleep(1800)




@app.route("/")
def home():

    return "AI CRYPTO BOT RUNNING"





def start():

    t=threading.Thread(
        target=market_scan
    )

    t.start()





if __name__=="__main__":


    print("BOT STARTED")


    start()


    app.run(
        host="0.0.0.0",
        port=10000
    )
