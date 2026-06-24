import os
import time
import threading
import requests
import pandas as pd

from flask import Flask
from binance.client import Client
import ta


app = Flask(__name__)


API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


client = Client(API_KEY, API_SECRET)


BLOCKED = [
    "USDT",
    "USDC",
    "TUSD",
    "FDUSD",
    "PAX",
    "BUSD"
]


def send_msg(text):

    try:

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=10
        )

    except Exception as e:
        print(e)



def get_analysis(symbol):

    try:

        candles = client.get_klines(
            symbol=symbol,
            interval="15m",
            limit=100
        )


        df = pd.DataFrame(
            candles,
            columns=[
                "time","open",
                "high","low",
                "close",
                "volume",
                "x1","x2",
                "x3","x4",
                "x5","x6"
            ]
        )


        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)



        price = df["close"].iloc[-1]


        rsi = ta.momentum.RSIIndicator(
            df["close"]
        ).rsi().iloc[-1]


        ema20 = ta.trend.EMAIndicator(
            df["close"],20
        ).ema_indicator().iloc[-1]


        ema50 = ta.trend.EMAIndicator(
            df["close"],50
        ).ema_indicator().iloc[-1]



        score = 0
        reasons=[]



        # Trend

        if ema20 > ema50:

            score +=2
            reasons.append(
                "Trend yükseliş"
            )



        # RSI

        if 40 < rsi < 70:

            score+=2
            reasons.append(
                "RSI sağlam zona"
            )

        elif rsi >=70:

            reasons.append(
                "RSI qızıb"
            )



        # Volume

        volume_now=df["volume"].iloc[-1]

        volume_avg=df["volume"].mean()


        if volume_now > volume_avg:

            score+=2
            reasons.append(
                "Volume artır"
            )



        # Momentum

        old=df["close"].iloc[-10]


        change=((price-old)/old)*100


        if change > 1:

            score+=2
            reasons.append(
                "Momentum güclü"
            )



        # Likvidlik

        if volume_avg > 100000:

            score+=1
            reasons.append(
                "Likvidlik yaxşı"
            )



        if rsi < 65:

            score+=1



        return {

            "symbol":symbol,
            "price":price,
            "rsi":round(rsi,2),
            "score":score,
            "change":round(change,2),
            "reasons":reasons

        }



    except Exception:

        return None





def btc_check():

    try:

        data=get_analysis("BTCUSDT")

        if data and data["score"]>=5:

            return "🟢 BTC vəziyyəti normal"

        return "⚠️ BTC zəif"


    except:

        return "BTC analiz yoxdur"






def scan():

    results=[]


    tickers=client.get_ticker()



    for t in tickers:


        symbol=t["symbol"]



        if not symbol.endswith("USDT"):

            continue



        if any(x in symbol for x in BLOCKED):

            continue



        data=get_analysis(symbol)



        if data and data["score"]>=6:

            results.append(data)



    results.sort(
        key=lambda x:x["score"],
        reverse=True
    )


    return results[:8]





def report():

    coins=scan()


    msg="🧠 AI CRYPTO ANALYST V2.2\n\n"

    msg+=btc_check()

    msg+="\n\n"



    if not coins:

        msg+="👀 Hazırda güclü fürsət yoxdur\n"

        return msg




    for c in coins:


        if c["score"]>=8:

            status="🚀 FÜRSƏT"

        else:

            status="👀 İZLƏMƏ"



        msg+=f"""
{status}

{c['symbol']}

Qiymət:
{c['price']}

Score:
{c['score']}/10

RSI:
{c['rsi']}

Momentum:
{c['change']}%

Səbəb:
{", ".join(c['reasons'])}

Plan:
🟢 30% giriş
🟡 geri çəkilmədə əlavə
🔴 risk idarəsi vacib


"""


    return msg





def bot_loop():

    time.sleep(10)


    send_msg(
        "🤖 AI Crypto Analyst V2.2 başladı"
    )



    while True:


        send_msg(
            report()
        )


        time.sleep(300)





@app.route("/")
def home():

    return "AI Crypto Analyst Running"



threading.Thread(
    target=bot_loop,
    daemon=True
).start()



app.run(
    host="0.0.0.0",
    port=int(
        os.getenv(
            "PORT",
            10000
        )
    )
)
