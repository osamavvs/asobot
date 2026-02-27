import asyncio
import pyrogram.errors

# هذا الكود يمنع انهيار البوت إذا لم يجد تعريف الخطأ في المكتبة
try:
    from pyrogram.errors import GroupcallForbidden
except ImportError:
    # صنع الخطأ يدوياً في ذاكرة النظام لتجاوز مشكلة الاستيراد
    setattr(pyrogram.errors, "GroupcallForbidden", type("GroupcallForbidden", (Exception,), {}))

from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL
from config import API_ID, API_HASH, BOT_TOKEN

# تعريف البوت والمحرك
app = Client("CristalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)
