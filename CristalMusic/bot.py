import asyncio
import yt_dlp
import json
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN

# --- الإعدادات الأساسية ---
OWNER_ID = 8074717568 
app = Client("CristalMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# --- نظام الملفات ---
STATS_FILE = "stats.json"
BANNED_FILE = "banned.json"

def load_data(file, default):
    if not os.path.exists(file): return default
    with open(file, "r") as f:
        try: return json.load(f)
        except: return default

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f)

stats = load_data(STATS_FILE, {"users": [], "groups": []})
banned_users = load_data(BANNED_FILE, [])

# --- إعدادات المستخرج (الحل السحري للتشغيل) ---
YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "geo_bypass": True,
}

# --- نظام التشغيل المستقر ---
@app.on_message(filters.text & filters.regex(r"^(شغل|تشغيل)\s+(.*)"))
async def play_handler(client, message):
    # منع المحظورين
    if message.from_user.id in banned_users:
        return await message.reply_text("🚫 أنت محظور من استخدام البوت.")

    # تحديث الإحصائيات
    chat_id = message.chat.id
    if str(chat_id) not in stats["groups"] and message.chat.type != "private":
        stats["groups"].append(str(chat_id))
        save_data(STATS_FILE, stats)

    query = message.matches[0].group(2)
    m = await message.reply_text("🔎 **جاري البحث والتحميل بأقصى سرعة...**")

    try:
        # البحث عن الفيديو
        search = VideosSearch(query, limit=1)
        res = search.result()['result'][0]
        video_url = res['link']
        title = res['title']
        thumb = res['thumbnails'][0]['url']

        # استخراج رابط الصوت الخام (Direct Stream)
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            audio_url = info['url']

        # محاولة الانضمام للمكالمة وتشغيل الصوت
        try:
            await call_py.join_group_call(
                chat_id, 
                MediaStream(audio_url)
            )
        except Exception as e:
            return await m.edit(f"❌ **تأكد من فتح المكالمة الصوتية أولاً!**\nالسبب: `{e}`")

        await m.delete()
        await message.reply_photo(
            photo=thumb,
            caption=f"**✅ تم التشغيل بنجاح**\n\n**📌 العنوان:** `{title}`\n**👤 بواسطة:** {message.from_user.mention}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏸ مؤقت", callback_data="pause"), InlineKeyboardButton("▶️ استئناف", callback_data="resume")],
                [InlineKeyboardButton("⏹ إيقاف", callback_data="stop")]
            ])
        )

    except Exception as e:
        await m.edit(f"⚠️ **حدث خطأ أثناء التشغيل:**\nربما يوتيوب قام بحظر السيرفر مؤقتاً.\nالسبب: `{e}`")

# --- لوحة التحكم ---
@app.on_message(filters.regex("^التحكم$") & filters.user(OWNER_ID))
async def admin_panel(client, message):
    await message.reply_text(
        f"📊 **إحصائيات Cristal:**\n\n👥 مستخدمين: `{len(stats['users'])}`\n🏘 مجموعات: `{len(stats['groups'])}`",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 تحديث", callback_data="refresh")]])
    )

# --- معالجة الأزرار ---
@app.on_callback_query()
async def cb_handler(client, query):
    if query.data == "stop":
        await call_py.leave_group_call(query.message.chat.id)
        await query.message.delete()
    elif query.data == "pause":
        await call_py.pause_stream(query.message.chat.id)
        await query.answer("تم الإيقاف المؤقت")
    elif query.data == "resume":
        await call_py.resume_stream(query.message.chat.id)
        await query.answer("تم الاستئناف")

async def main():
    await app.start()
    await call_py.start()
    print("🚀 البوت يعمل الآن بأفضل نسخة مستقرة!")
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
