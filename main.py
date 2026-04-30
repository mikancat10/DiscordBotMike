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
    if now.hour == 8 and now.minute == 0:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            weather = get_weather()
            news = get_news()
            msg = f"おはようございます！8時になりました。\n\n【天気】\n{weather}\n\n【最新ニュース】\n{news}"
            await channel.send(msg)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    daily_report.start() # スケジュール処理を開始

# Renderでポートを待機させるためのダミーサーバー（これがないとRenderで落ちることがあります）
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()
client.run(TOKEN)
