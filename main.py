import discord
from discord.ext import tasks
import datetime
import requests
import os
from flask import Flask
from threading import Thread

# --- 設定項目 ---
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID')) if os.getenv('CHANNEL_ID') else None

# 天気API：東京のコードは 130010
WEATHER_URL = "[https://weather.tsukumijima.net/api/forecast/city/130010](https://weather.tsukumijima.net/api/forecast/city/130010)"
# ニュースAPI：URLだけでJSONが取れる公開APIを想定（例）
NEWS_URL = "[https://api.hatchful.jp/v1/news](https://api.hatchful.jp/v1/news)" # サンプルURLです

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def get_info_from_url():
    """URLを叩いてJSONを取得し、メッセージを組み立てる"""
    try:
        # 1. 天気情報の取得
        w_res = requests.get(WEATHER_URL).json()
        today = w_res['forecasts'][0]
        weather_text = f"今日の天気は「{today['telop']}」、最高気温は {today['temperature']['max']['Celsius']}℃ です。"
        
        # 2. ニュース情報の取得（例としてGoogle News RSS等を想定）
        # ※もし特定のURL形式があればここに差し替えてください
        n_res = requests.get("[https://sumai-kyun.com/api/news/](https://sumai-kyun.com/api/news/)").json() # 公開されているJSON API例
        news_list = [f"・{item['title']}" for item in n_res[:3]]
        news_text = "\n".join(news_list)
        
        return f"{weather_text}\n\n【最新ニュース】\n{news_text}"
    except Exception as e:
        return f"情報の取得に失敗しました: {e}"

@tasks.loop(seconds=60)
async def daily_report():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    # 日本時間の 08:00 に実行
    if now.hour == 17 and now.minute == 57:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            content = get_info_from_url()
            await channel.send(f"おはようございます！\n{content}")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    if not daily_report.is_running():
        daily_report.start()

# --- Render用ウェブサーバー ---
app = Flask('')
@app.route('/')
def home(): return "OK"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(TOKEN)
