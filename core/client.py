from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

# محاولة الاستدعاء بأكثر من طريقة لضمان التوافق مع أي نسخة مثبتة
try:
    # الطريقة للنسخ الحديثة جداً (v3+)
    from pytgcalls.pytgcalls import PyTgCalls
except ImportError:
    try:
        # الطريقة للنسخ المستقرة (v2)
        from pytgcalls import PyTgCalls
    except ImportError:
        # حل أخير في حال فشل الاستدعاء المباشر
        import pytgcalls
        PyTgCalls = pytgcalls.PyTgCalls

# تهيئة التطبيق
app = Client("CristalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# تهيئة مشغل المكالمات
call_py = PyTgCalls(app)
