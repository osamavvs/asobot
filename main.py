import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from pytgcalls.types.stream import StreamAudioQuality
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN, FORCE_SUB

# تعريف البوت ومشغل الصوت
app = Client("CrystalMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

# إعدادات استخراج الصوت من اليوتيوب
ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
}

# دالة البحث وجلب الرابط
async def get_audio_info(query):
    search = VideosSearch(query, limit=1)
    results = search.result()["result"]
    if not results:
        return None, None
    link = results[0]["link"]
    title = results[0]["title"]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        return info["url"], title

@app.on_message(filters.command("start"))
async def start_handler(_, message):
    await message.reply(
        "✨ **مرحباً بك في بوت كريستال الموسيقي**\n\n"
        "• لتشغيل أغنية: `/play` اسم الأغنية\n"
        "• لإيقاف التشغيل: `/stop`"
    )

@app.on_message(filters.command("play") & filters.group)
async def play_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ **يرجى كتابة اسم الأغنية بعد الأمر!**")
    
    m = await message.reply("🔎 **جاري البحث والمعالجة...**")
    query = " ".join(message.command[1:])
    
    try:
        audio_url, title = await get_audio_info(query)
        if not audio_url:
            return await m.edit("❌ **لم يتم العثور على نتائج.**")
        
        # الانضمام للمكالمة وتشغيل الصوت بجودة عالية
        await call.join_group_call(
            message.chat.id, 
            AudioPiped(audio_url, StreamAudioQuality.HIGH)
        )
        await m.edit(f"▶️ **تم التشغيل بنجاح:**\n`{title}`")
    except Exception as e:
        await m.edit(f"❌ **حدث خطأ أثناء التشغيل:**\n`{str(e)}`")

@app.on_message(filters.command("stop") & filters.group)
async def stop_handler(_, message):
    try:
        await call.leave_group_call(message.chat.id)
        await message.reply("⏹ **تم إيقاف التشغيل بنجاح.**")
    except:
        await message.reply("❌ **البوت غير متصل بمكالمة حالياً.**")

async def start_bot():
    await app.start()
    await call.start()
    print("✅ Crystal Music Bot is Online!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_bot())
