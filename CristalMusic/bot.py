import asyncio
import yt_dlp
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from youtubesearchpython import VideosSearch

# استدعاء الكلاينت من مجلد الـ core
from core.client import app, call_py
from config import OWNER_ID, OWNER_USER, CHANNEL_USER

# إضافة هذا السطر لاستيراد أنواع الوسائط بشكل صحيح
from pytgcalls.types import MediaStream 

# ... باقي الكود كما هو ...
import asyncio
import yt_dlp
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from youtubesearchpython import VideosSearch

# استدعاء الكلاينت من مجلد الـ core
from core.client import app, call_py
from config import OWNER_ID, OWNER_USER, CHANNEL_USER

START_IMG = "https://telegra.ph/file/07f43f11f568a91439d5b.jpg"

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if message.from_user.id == OWNER_ID:
        await message.reply_photo(photo=START_IMG, caption=f"⚡️ أهلاً بك مطورنا @{OWNER_USER} في لوحة التحكم.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 لوحة الأوامر", callback_data="cmds")]]))
    else:
        await message.reply_photo(photo=START_IMG, caption=f"👋 أهلاً بك {message.from_user.mention}\nأنا بوت كرستال للموسيقى.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎮 الأوامر", callback_data="cmds")]]))

@app.on_message(filters.regex(r"^(شغل|تشغيل)\s+(.*)"))
async def play(client, message):
    query = message.matches[0].group(2)
    m = await message.reply_text("🔎 جاري البحث...")
    try:
        search = VideosSearch(query, limit=1).result()['result'][0]
        ydl_opts = {"format": "bestaudio[ext=m4a]", "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            audio_url = ydl.extract_info(search['link'], download=False)['url']
        
        from pytgcalls.types import MediaStream
        await call_py.join_group_call(message.chat.id, MediaStream(audio_url))
        await m.edit(f"✅ تم التشغيل: **{search['title']}**")
    except Exception as e:
        await m.edit(f"❌ خطأ: {e}")

# دالة تشغيل البوت
async def main():
    await app.start()
    await call_py.start()
    print("💎 البوت يعمل الآن!")
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    app.run(main())
