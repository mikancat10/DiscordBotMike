import discord
from discord.ext import tasks
import datetime
import requests
import os
import discord

# --- 直接書かずに、Renderの設定から呼び出す ---
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID') # IDも環境変数にするのがおすすめ

# あとはこれを使ってログインするだけ
client = discord.Client(intents=discord.Intents.default())
# ...中略...
client.run(TOKEN)
# --- 設定項目 ---
WEATHER_API_KEY = os.getenv('18fa7106d25ea086fd96b290398bdb9f')
NEWS_API_KEY = os.getenv('312c3568831b4fb588b1ab9daeeecd1f')
CITY_NAME = "Tokyo" # 取得したい都市名

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={WEATHER_API_KEY}&lang=ja&units=metric"
    res = requests.get(url).json()
    description = res['weather'][0]['description']
    temp = res['main']['temp']
    return f"今日の{CITY_NAME}の天気は「{description}」、気温は {temp}℃ です。"

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=jp&apiKey={NEWS_API_KEY}&pageSize=3"
    res = requests.get(url).json()
    articles = res.get('articles', [])
    news_list = [f"・{a['title']}" for a in articles]
    return "\n".join(news_list)

@tasks.loop(seconds=60)
async def daily_report():
    # 日本時間 (UTC+9) で 08:00 かチェック
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    if now.hour == 17 and now.minute == 30:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            weather = get_weather()
            news = get_news()
            msg = f"これは試験です　おはようございます！8時になりました。\n\n【天気】\n{weather}\n\n【最新ニュース】\n{news}"
            await channel.send(msg)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    daily_report.start() # スケジュール処理を開始

# Renderでポートを待機させるためのダミーサーバー（これがないとRenderで落ちることがあります）
# ... 前半のコード（get_weather, get_news, daily_reportなど）はそのまま ...

from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    # Renderは環境変数 PORT を指定してくるので、それを優先する
    port = int(os.environ.get("PORT", 8080))
    # debug=False, use_reloader=False にしてスレッド内での安定性を高める
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # 1. 先にFlask（ウェブサーバー）を別スレッドで起動
    t = Thread(target=run_flask)
    t.daemon = True # メインプログラム終了時に一緒に終了するように設定
    t.start()
    print("Flask server started.")

    # 2. その後にDiscordボットを起動（これは無限ループになるので最後に書く）
    try:
        client.run(TOKEN)
    except Exception as e:
        print(f"Error starting bot: {e}")
