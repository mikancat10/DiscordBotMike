import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- 設定項目 ---
DISCORD_TOKEN = 'あなたのボットトークンをここに貼り付け'
CHANNEL_ID = 1234567890  # 監視したいDiscordチャンネルのID（数値）
# ----------------

# Firebaseの初期化
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Discord Botの初期化
intents = discord.Intents.default()
intents.message_content = True  # メッセージ内容を読み取る設定
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'ログインしました: {bot.user.name}')

@bot.event
async def on_message(message):
    # ボット自身の発言は無視、かつ指定したチャンネルのみ監視
    if message.author.bot:
        return
    if message.channel.id != CHANNEL_ID:
        return

    try:
        # Firebase (Firestore) にデータを追加
        doc_ref = db.collection('discord_messages').document()
        doc_ref.set({
            'user': message.author.display_name,
            'content': message.content,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'time': datetime.now().strftime("%H:%M"),
            'avatar': str(message.author.display_avatar.url) # アイコンURLもついでに保存
        })
        print(f'保存成功: {message.author.display_name} - {message.content}')
    except Exception as e:
        print(f'エラーが発生しました: {e}')

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
