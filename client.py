from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
import pytgcalls

# فحص النسخة ديناميكياً وتحديد الكلاينت المناسب
if hasattr(pytgcalls, "Client"):
    # إذا كانت النسخة v3
    PyTgCalls = pytgcalls.Client
elif hasattr(pytgcalls, "PyTgCalls"):
    # إذا كانت النسخة v2
    PyTgCalls = pytgcalls.PyTgCalls
else:
    # حل احتياطي أخير
    from pytgcalls import PyTgCalls

app = Client("CristalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)
