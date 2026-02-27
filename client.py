from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from pytgcalls import PyTgCalls  # النسخة 2.x تستخدم هذا الاسم فقط

app = Client("CristalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)
