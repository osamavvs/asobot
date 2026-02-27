from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

# استدعاء المكتبة بطريقة ذكية لتجنب خطأ الـ ImportError
try:
    # الطريقة الحديثة (v3)
    from pytgcalls.pytgcalls import PyTgCalls
except ImportError:
    try:
        # الطريقة التقليدية (v2)
        from pytgcalls import PyTgCalls
    except ImportError:
        # في حال فشل كل شيء، نستخدم استدعاءً مباشراً
        import pytgcalls
        PyTgCalls = pytgcalls.PyTgCalls

# تهيئة التطبيق
app = Client("CristalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# تهيئة مشغل المكالمات
call_py = PyTgCalls(app)
