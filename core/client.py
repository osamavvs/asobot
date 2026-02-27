from pyrogram import Client
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, BOT_TOKEN

# تهيئة تطبيق التليجرام
app = Client("CristalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# تهيئة مشغل المكالمات (باستخدام الاستدعاء الصحيح للنسخة الحديثة)
call_py = PyTgCalls(app)
