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


bot = Bot(TOKEN)

client = Client()



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
            "Telegram error:",
            e
        )





def analyze(symbol):

    try:

        candles = client.get_klines(
            symbol=symbol,
            interval="1h",
            limit=120
        )


        df = pd.DataFrame(candles)


        close = df[4].astype(float)

        volume = df[5].astype(float)


        price = close.iloc[-1]


        rsi = ta.momentum.RSIIndicator(
            close
        ).rsi().iloc[-1]


        ema20 = close.ewm(
            span=20
        ).mean().iloc[-1]


        ema50 = close.ewm(
            span=50
        ).mean().iloc[-1]



        score = 0

        reasons = []



        if ema20 > ema50:

            score += 3

            reasons.append(
                "Trend UP"
            )



        if price > ema20:

            score += 2

            reasons.append(
                "Qiymet guclu"
            )



        if 50 < rsi < 70:

            score += 2

            reasons.append(
                "Momentum"
            )



        if volume.iloc[-1] > volume.mean():

            score += 2

            reasons.append(
                "Volume artib"
            )



        return (
            price,
            rsi,
            score,
            reasons
        )



    except Exception as e:

        print(
            "ANALYZE ERROR",
            symbol,
            e
        )

        return None





def scanner():


    print(
        "SCANNER STARTED"
    )


    while True:


        try:


            info = client.get_exchange_info()


            print(
                "BINANCE CONNECTED"
            )



            coins = []



            for x in info["symbols"]:


                if (
                    x["quoteAsset"] == "USDT"
                    and x["status"] == "TRADING"
                ):


                    coins.append(
                        x["symbol"]
                    )



            print(
                "TOTAL COINS:",
                len(coins)
            )



            signals = []



            for coin in coins[:300]:


                print(
                    "Checking:",
                    coin
                )



                data = analyze(coin)



                if data:


                    price, rsi, score, reasons = data



                    if score >= 7:


                        signals.append(
                            (
                                score,
                                coin,
                                price,
                                rsi,
                                reasons
                            )
                        )



            signals.sort(
                reverse=True
            )



            msg = (
                "🧠 AI CRYPTO ANALYST V2.5\n\n"
            )



            if signals:


                for s in signals[:10]:


                    msg += (

                        f"🚀 {s[1]}\n"
                        f"💰 Qiymət: {round(s[2],6)}\n"
                        f"📊 RSI: {round(s[3],2)}\n"
                        f"⭐ Score: {s[0]}/9\n"
                        f"✅ {', '.join(s[4])}\n\n"

                    )


            else:


                msg += (
                    "⏳ Güclü setup yoxdur\n"
                    "Bazar skan edilir..."
                )



            print(msg)


            send(msg)



        except Exception as e:


            print(
                "SCAN ERROR:",
                e
            )



        time.sleep(60)







@app.route("/")
def home():

    return "AI V2.5 RUNNING"






def start():


    t = threading.Thread(
        target=scanner
    )


    t.daemon = True


    t.start()







if __name__ == "__main__":


    print(
        "AI V2.5 STARTED"
    )


    start()



    app.run(
        host="0.0.0.0",
        port=10000
    )
