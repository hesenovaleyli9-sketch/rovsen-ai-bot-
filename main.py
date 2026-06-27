import os
import time
import threading
import asyncio
import pandas as pd

from flask import Flask
from binance.client import Client
from telegram import Bot
import ta


app = Flask(__name__)


TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


print("TOKEN CHECK:", TOKEN)
print("CHAT CHECK:", CHAT_ID)


if not TOKEN:
    raise Exception("TOKEN yoxdur. Render Environment yoxla")


if not CHAT_ID:
    raise Exception("CHAT_ID yoxdur. Render Environment yoxla")



bot = Bot(TOKEN)

client = Client()



# =========================
# TELEGRAM
# =========================

def send(message):

    async def send_async():

        await bot.send_message(
            chat_id=CHAT_ID,
            text=message
        )


    try:

        loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)

        loop.run_until_complete(
            send_async()
        )

        loop.close()


    except Exception as e:

        print(
            "TELEGRAM ERROR:",
            e
        )





# =========================
# ANALYSIS
# =========================

def analyze(symbol):

    try:

        candles = client.get_klines(
            symbol=symbol,
            interval="15m",
            limit=100
        )


        df = pd.DataFrame(candles)


        close = df[4].astype(float)

        volume = df[5].astype(float)


        price = close.iloc[-1]


        ema20 = close.ewm(
            span=20
        ).mean().iloc[-1]


        ema50 = close.ewm(
            span=50
        ).mean().iloc[-1]


        rsi = ta.momentum.RSIIndicator(
            close
        ).rsi().iloc[-1]



        score = 0

        reasons=[]



        if ema20 > ema50:

            score += 2

            reasons.append(
                "Trend UP"
            )



        if price > ema20:

            score += 2

            reasons.append(
                "Price strength"
            )



        if 45 < rsi < 70:

            score += 2

            reasons.append(
                "Momentum"
            )



        if volume.iloc[-1] > volume.mean()*1.8:

            score += 3

            reasons.append(
                "Volume Spike"
            )



        return {

            "symbol":symbol,
            "price":price,
            "rsi":rsi,
            "score":score,
            "reasons":reasons

        }



    except Exception as e:

        print(
            "ANALYZE ERROR:",
            symbol,
            e
        )

        return None





# =========================
# SCANNER
# =========================

def scanner():


    print(
        "SCANNER STARTED"
    )


    while True:


        try:


            print(
                "NEW SCAN"
            )


            info = client.get_exchange_info()


            coins=[]



            for x in info["symbols"]:


                if (
                    x["quoteAsset"]=="USDT"
                    and x["status"]=="TRADING"
                ):


                    coins.append(
                        x["symbol"]
                    )



            print(
                "TOTAL COINS:",
                len(coins)
            )



            signals=[]



            for coin in coins[:200]:


                print(
                    "CHECK:",
                    coin
                )



                result = analyze(
                    coin
                )



                if result and result["score"] >= 7:

                    signals.append(
                        result
                    )




            msg = "🧠 AI CRYPTO ANALYST V2.5\n\n"



            if signals:


                for s in signals[:10]:


                    msg += (

                    f"🚀 {s['symbol']}\n"
                    f"💰 {round(s['price'],6)}\n"
                    f"📊 RSI {round(s['rsi'],2)}\n"
                    f"⭐ Score {s['score']}/9\n"
                    f"✅ {', '.join(s['reasons'])}\n\n"

                    )


            else:


                msg += (
                    "⏳ Setup yoxdur\n"
                    "Skan davam edir..."
                )



            print(msg)


            send(msg)



        except Exception as e:


            print(
                "SCANNER ERROR:",
                e
            )



        time.sleep(300)





@app.route("/")
def home():

    return "AI V2.5 RUNNING"





def start():


    t = threading.Thread(
        target=scanner
    )


    t.daemon=True

    t.start()





if __name__=="__main__":


    print(
        "AI V2.5 STARTED"
    )


    start()


    app.run(
        host="0.0.0.0",
        port=10000
    )
