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
            limit=120
        )


        df = pd.DataFrame(
            candles,
            columns=[
                "time","open","high","low",
                "close","volume",
                "x1","x2","x3",
                "x4","x5","x6"
            ]
        )


        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)


        price = df.close.iloc[-1]


        rsi = ta.momentum.RSIIndicator(
            df.close
        ).rsi().iloc[-1]


        ema20 = ta.trend.EMAIndicator(
            df.close,20
        ).ema_indicator().iloc[-1]


        ema50 = ta.trend.EMAIndicator(
            df.close,50
        ).ema_indicator().iloc[-1]



        volume_now = df.volume.iloc[-1]

        volume_avg = df.volume.mean()



        change = (
            (price-df.close.iloc[-10])
            /
            df.close.iloc[-10]
        )*100



        score = 0

        reasons=[]



        if ema20 > ema50:

            score += 3

            reasons.append(
                "Trend yuxarı"
            )


        if volume_now > volume_avg*1.3:

            score += 2

            reasons.append(
                "Volume artır"
            )


        if 45 < rsi < 65:

            score += 2

            reasons.append(
                "RSI ideal"
            )


        if 1 < change < 8:

            score += 2

            reasons.append(
                "Erkən momentum"
            )


        if change > 15:

            score -= 2

            reasons.append(
                "Artıq qalxıb"
            )



        return {

            "symbol":symbol,
            "price":price,
            "score":score,
            "rsi":round(rsi,2),
            "change":round(change,2),
            "reasons":reasons

        }



    except:

        return None





def scan_market():


    result=[]


    tickers = client.get_ticker()


    for t in tickers:


        symbol=t["symbol"]


        if not symbol.endswith("USDT"):

            continue



        if "UP" in symbol or "DOWN" in symbol:

            continue



        data=analyze(symbol)


        if data and data["score"]>=5:

            result.append(data)



    result.sort(
        key=lambda x:x["score"],
        reverse=True
    )


    return result[:10]





def create_report():


    coins=scan_market()



    msg="""
🧠 AI CRYPTO SCANNER V3

Bazarda erkən fürsətlər axtarılır...

"""



    if not coins:

        msg+="
Hazırda uyğun siqnal yoxdur"

        return msg



    for c in coins:


        if c["score"]>=7:

            title="🚀 GİRİŞƏ YAXIN"

        else:

            title="👀 NƏZARƏT"



        msg+=f"""

{title}

{c['symbol']}

Qiymət:
{c['price']}

Score:
{c['score']}/10

RSI:
{c['rsi']}

Hərəkət:
{c['change']}%

Səbəb:
{", ".join(c['reasons'])}


Plan:
🟢 Hissəli giriş
🟡 Geri çəkilmə izlənir
🔴 Risk idarəsi


"""


    return msg





def bot_loop():


    time.sleep(10)


    send_msg(
        "🚀 AI Crypto Scanner V3 başladı"
    )



    while True:


        send_msg(
            create_report()
        )


        time.sleep(300)





@app.route("/")
def home():

    return "AI Scanner V3 Running"





threading.Thread(
    target=bot_loop,
    daemon=True
).start()



app.run(
    host="0.0.0.0",
    port=int(os.getenv("PORT",10000))
)
