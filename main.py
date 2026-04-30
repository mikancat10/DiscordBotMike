import discord
from discord.ext import tasks
import datetime
import requests
import os
from flask import Flask
from threading import Thread

# --- 設定項目（RenderのEnvironment Variablesで設定した名前を入れる） ---
TOKEN = os.getenv('DISCORD_TOKEN')
# CHANNEL_ID は数値である必要があるため int() で変換
CHANNEL_ID_STR = os.getenv('CHANNEL_ID')
CHANNEL_ID = int(CHANNEL_ID_STR) if CHANNEL_ID_STR else None

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
CITY_NAME = "Tokyo"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def get_weather():
    if not WEATHER_API_KEY:
        return "天気APIキーが設定されていません。"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={WEATHER_API_KEY}&lang=ja&units=metric"
    res = requests.get(url).json()
    try:
        description = res['weather'][0]['description']
        temp = res['main']['temp']
        return f"今日の{CITY_NAME}の天気は「{description}」、気温は {temp}℃ です。"
    except:
        return "天気情報の取得に失敗しました。"

def get_news():
    if not NEWS_API_KEY:
        return "ニュースAPIキーが設定されていません。"
    url = f"https://newsapi.org/v2/top-headlines?country=jp&apiKey={NEWS_API_KEY}&pageSize=3"
    res = requests.get(url).json()
    try:
        articles = res.get('articles', [])
        news_list = [f"・{a['title']}" for a in articles]
        return "\n".join(news_list) if news_list else "ニュースが見つかりませんでした。"
    except:
        return "ニュースの取得に失敗しました。"

@tasks.loop(seconds=60)
async def daily_report():
    # 日本時間 (UTC+9) で 17:30 かチェック（試験用設定）
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    if now.hour == 17 and now.minute == 30:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            weather = get_weather()
            news = get_news()
            msg = f"これは試験です。おはようございます！\n\n【天気】\n{weather}\n\n【最新ニュース】\n{news}"
            await channel.send(msg)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    if not daily_report.is_running():
        daily_report.start()

# --- Render用ダミーサーバー設定 ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Flaskを別スレッドで起動
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Discordボットを起動
    if TOKEN:
        try:
            client.run(TOKEN)
        except Exception as e:
            print(f"Error starting bot: {e}")
    else:
        print("DISCORD_TOKEN が設定されていません。")
