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



def send(msg):

    try:

        bot.send_message(
            chat_id=CHAT_ID,
            text=msg
        )

    except Exception as e:

        print("Telegram:", e)




def analyze(symbol):

    try:

        candles = client.get_klines(
            symbol=symbol,
            interval="1h",
            limit=150
        )


        df = pd.DataFrame(candles)


        df["close"] = df[4].astype(float)
        df["volume"] = df[5].astype(float)


        close = df["close"]
        volume = df["volume"]


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


        vol_now = volume.iloc[-1]

        vol_avg = volume.mean()


        score = 0

        reasons = []


        if ema20 > ema50:

            score += 3
            reasons.append("Trend yuxarı")


        if price > ema20:

            score += 2
            reasons.append("Qiymət güclü")


        if 50 < rsi < 70:

            score += 2
            reasons.append("Momentum yaxşı")


        if vol_now > vol_avg:

            score += 2
            reasons.append("Volume artıb")


        return (
            price,
            rsi,
            score,
            reasons
        )


    except:

        return None






def scanner():


    while True:


        try:


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



            signals=[]



            for coin in coins[:400]:


                data = analyze(coin)


                if data:


                    price,rsi,score,reasons=data



                    if score >=7:


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



            msg = "🧠 AI CRYPTO ANALYST V2.5\n\n"



            if signals:


                for s in signals[:10]:


                    msg += (
                    f"🚀 {s[1]}\n"
                    f"💰 Qiymət: {round(s[2],6)}\n"
                    f"📊 RSI: {round(s[3],2)}\n"
                    f"⭐ Güc: {s[0]}/9\n"
                    f"✅ {', '.join(s[4])}\n"
                    f"🎯 STATUS: İzləmə / Giriş yaxın\n\n"
                    )


            else:


                msg += (
                "⏳ Güclü setup yoxdur\n"
                "Bazar analiz edilir..."
                )



            send(msg)



        except Exception as e:

            print(e)



        time.sleep(1800)






@app.route("/")
def home():

    return "AI V2.5 ACTIVE"





def start():

    t=threading.Thread(
        target=scanner
    )

    t.daemon=True

    t.start()





if __name__=="__main__":


    print("AI V2.5 STARTED")


    start()


    app.run(
        host="0.0.0.0",
        port=10000
    )
