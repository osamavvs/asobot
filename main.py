import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# حل مشكلة الاستدعاء في هيروكو
from pytgcalls.pytgcalls import PyTgCalls 
from pytgcalls.types import AudioPiped
from pytgcalls.types.stream import StreamAudioQuality

from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN, FORCE_SUB

app = Client("CrystalMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

ydl_opts = {"format": "bestaudio/best", "quiet": True, "nocheckcertificate": True}

async def get_audio_info(query):
    search = VideosSearch(query, limit=1)
    results = search.result()["result"]
    if not results: return None, None
    link, title = results[0]["link"], results[0]["title"]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        return info["url"], title

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply("✨ **أهلاً بك في سورس كريستال**\nاستخدم /play للتشغيل.")

@app.on_message(filters.command("play") & filters.group)
async def play(client, message):
    if len(message.command) < 2: return await message.reply("❌ اكتب اسم الأغنية.")
    m = await message.reply("🔎 جاري البحث...")
    try:
        audio_url, title = await get_audio_info(" ".join(message.command[1:]))
        if not audio_url: return await m.edit("❌ لا توجد نتائج.")
        await call.join_group_call(message.chat.id, AudioPiped(audio_url, StreamAudioQuality.HIGH))
        await m.edit(f"▶️ **تم التشغيل:**\n`{title}`")
    except Exception as e:
        await m.edit(f"❌ حدث خطأ: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop(_, message):
    try:
        await call.leave_group_call(message.chat.id)
        await message.reply("⏹ تم الإيقاف.")
    except:
        await message.reply("❌ البوت غير متصل.")

async def run_bot():
    await app.start()
    await call.start()
    print("✅ Crystal Music Bot is Online!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run_bot())
