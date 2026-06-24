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


print("BOT START")
print("CHAT:", CHAT_ID)


# =========================
# TELEGRAM
# =========================

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



# =========================
# ANALYSIS
# =========================


def analyze_coin(symbol):

    try:


        candles = client.get_klines(
            symbol=symbol,
            interval="15m",
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
            "x1","x2","x3","x4","x5","x6"
            ]
        )


        df["close"] = df["close"].astype(float)


        rsi = ta.momentum.RSIIndicator(
            df["close"]
        ).rsi().iloc[-1]


        ema20 = ta.trend.EMAIndicator(
            df["close"],
            20
        ).ema_indicator().iloc[-1]


        ema50 = ta.trend.EMAIndicator(
            df["close"],
            50
        ).ema_indicator().iloc[-1]


        price = df["close"].iloc[-1]


        score = 0

        reasons = []


        if ema20 > ema50:

            score += 3
            reasons.append(
                "Trend yukarı"
            )


        if rsi < 70:

            score += 2
            reasons.append(
                "RSI normal"
            )


        if price > ema20:

            score += 2
            reasons.append(
                "Qiymət güclü"
            )



        return {

        "symbol":symbol,
        "price":price,
        "rsi":round(rsi,2),
        "score":score,
        "reasons":reasons

        }



    except Exception as e:

        print(symbol,e)

        return None



# =========================
# MARKET SCAN
# =========================


def scan():


    result=[]


    tickers = client.get_ticker()


    for t in tickers:


        symbol=t["symbol"]


        if not symbol.endswith("USDT"):
            continue


        try:


            data=analyze_coin(symbol)


            if data and data["score"]>=5:

                result.append(data)


        except:

            pass



    result.sort(
        key=lambda x:x["score"],
        reverse=True
    )


    return result[:5]



# =========================
# REPORT
# =========================


def report():


    coins=scan()


    if not coins:

        return "Hazırda güclü siqnal yoxdur"



    msg="🧠 AI MARKET ANALİZ\n\n"



    for c in coins:


        msg+=(
        f"🚀 {c['symbol']}\n"
        f"Qiymət: {c['price']}\n"
        f"RSI: {c['rsi']}\n"
        f"Score: {c['score']}/10\n"
        f"Səbəb: {', '.join(c['reasons'])}\n\n"
        )


    return msg




# =========================
# AUTO
# =========================


def loop():


    time.sleep(10)


    send_msg(
        "🤖 AI Scanner V2 başladı"
    )


    while True:


        send_msg(
            report()
        )


        time.sleep(300)




# =========================
# FLASK
# =========================


@app.route("/")

def home():

    return "AI Crypto Bot V2 Running"




threading.Thread(
    target=loop,
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
