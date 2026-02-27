from pyrogram import Client
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, BOT_TOKEN

# تهيئة تطبيق التليجرام
app = Client("CristalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# في النسخ الحديثة يتم الاستدعاء هكذا
call_py = PyTgCalls(app)
