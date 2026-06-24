import os
import time
import threading
import requests

from flask import Flask
from binance.client import Client


app = Flask(__name__)


# =========================
# ENV
# =========================

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


client = Client(API_KEY, API_SECRET)


print("TOKEN CHECK:", TELEGRAM_TOKEN[:10] if TELEGRAM_TOKEN else "NO TOKEN")
print("CHAT:", CHAT_ID)


# =========================
# TELEGRAM
# =========================

def send_msg(text):

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        r = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=10
        )

        print("TG:", r.text)

    except Exception as e:
        print("Telegram error:", e)



# =========================
# MARKET SCANNER
# =========================


def scan_market():

    results = []

    try:

        tickers = client.get_ticker()


        for coin in tickers:

            symbol = coin["symbol"]


            if not symbol.endswith("USDT"):
                continue


            if any(x in symbol for x in [
                "UP",
                "DOWN",
                "BULL",
                "BEAR"
            ]):
                continue



            try:

                change = float(
                    coin["priceChangePercent"]
                )


                volume = float(
                    coin["quoteVolume"]
                )


                price = float(
                    coin["lastPrice"]
                )


                score = 0


                if change > 3:
                    score += 3


                if volume > 10000000:
                    score += 3


                if change > 7:
                    score += 2


                if score >= 5:


                    results.append({

                        "symbol": symbol,
                        "price": price,
                        "change": change,
                        "volume": volume,
                        "score": score

                    })


            except:
                pass



        results.sort(
            key=lambda x:x["score"],
            reverse=True
        )


        return results[:10]



    except Exception as e:

        print("SCAN ERROR:",e)

        return []




# =========================
# FORMAT
# =========================


def create_report():

    coins = scan_market()


    if not coins:

        return "Hazırda güclü fürsət tapılmadı"



    msg = "🚀 MARKET FÜRSƏTLƏR\n\n"



    for c in coins:


        msg += (
            f"🔥 {c['symbol']}\n"
            f"Qiymət: {c['price']}\n"
            f"24h: {c['change']}%\n"
            f"Volume: {round(c['volume']/1000000,2)}M\n"
            f"Score: {c['score']}/10\n\n"
        )


    return msg




# =========================
# TELEGRAM COMMAND CHECK
# =========================


def telegram_loop():

    last_id = 0


    while True:


        try:

            url = (
            f"https://api.telegram.org/"
            f"bot{TELEGRAM_TOKEN}/getUpdates"
            )


            data = requests.get(
                url,
                timeout=20
            ).json()



            for item in data.get("result",[]):


                if item["update_id"] <= last_id:
                    continue


                last_id = item["update_id"]



                text = item.get(
                    "message",
                    {}
                ).get(
                    "text",
                    ""
                )


                if text == "/scan":


                    send_msg(
                        create_report()
                    )



                elif text == "/top":


                    send_msg(
                        create_report()
                    )



        except Exception as e:

            print(e)



        time.sleep(5)




# =========================
# AUTO SCAN
# =========================


def auto_scan():


    time.sleep(10)


    send_msg(
        "🤖 Scanner başladı"
    )


    while True:


        report = create_report()


        send_msg(report)


        time.sleep(300)




# =========================
# FLASK
# =========================


@app.route("/")

def home():

    return "AI Crypto Scanner Running"




# =========================
# START
# =========================


threading.Thread(
    target=auto_scan,
    daemon=True
).start()



threading.Thread(
    target=telegram_loop,
    daemon=True
).start()



port = int(
    os.environ.get(
        "PORT",
        10000
    )
)



app.run(
    host="0.0.0.0",
    port=port
)
