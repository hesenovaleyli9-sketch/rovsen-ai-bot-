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


# çıxarılacaq koinlər
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



def analyze(symbol):

    try:

        candles = client.get_klines(
            symbol=symbol,
            interval="15m",
            limit=100
        )


        df = pd.DataFrame(
            candles,
            columns=[
            "time","open","high",
            "low","close",
            "volume",
            "x1","x2","x3",
            "x4","x5","x6"
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


        volume_now = df["volume"].iloc[-1]
        volume_avg = df["volume"].mean()



        score = 0
        reasons=[]



        if ema20 > ema50:
            score +=3
            reasons.append(
                "Trend yukarı"
            )


        if rsi < 70:
            score +=2
            reasons.append(
                "RSI sağlam"
            )

        else:
            reasons.append(
                "RSI yüksək risk"
            )


        if volume_now > volume_avg:
            score+=3
            reasons.append(
                "Volume artımı"
            )



        change = (
            (price-df["close"].iloc[-5])
            /
            df["close"].iloc[-5]
        )*100



        if change > 2:
            score+=1
            reasons.append(
                "Momentum güclü"
            )



        return {

        "symbol":symbol,
        "price":price,
        "rsi":round(rsi,2),
        "score":score,
        "change":round(change,2),
        "reasons":reasons

        }


    except:

        return None




def scan():

    result=[]


    info=client.get_ticker()


    for x in info:


        symbol=x["symbol"]


        if not symbol.endswith("USDT"):
            continue


        if any(
            a in symbol
            for a in BLOCKED
        ):
            continue


        data=analyze(symbol)


        if data and data["score"]>=6:

            result.append(data)



    result.sort(
        key=lambda x:x["score"],
        reverse=True
    )


    return result[:5]





def create_report():


    coins=scan()


    if not coins:

        return "Hazırda güclü fürsət yoxdur"



    msg="🚀 SMART MARKET ANALİZ\n\n"



    for c in coins:


        msg+=f"""
🔥 {c['symbol']}

Qiymət:
{c['price']}

24h Momentum:
{c['change']}%

RSI:
{c['rsi']}

Score:
{c['score']}/10

Analiz:
{', '.join(c['reasons'])}

Plan:
🟢 Hissəli giriş düşünülə bilər
⚠️ Risk idarəsi vacibdir


"""



    return msg





def bot_loop():


    time.sleep(10)


    send_msg(
        "🤖 AI Scanner V2.1 aktivdir"
    )


    while True:


        send_msg(
            create_report()
        )


        time.sleep(300)





@app.route("/")
def home():

    return "AI Crypto Bot Running"



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
