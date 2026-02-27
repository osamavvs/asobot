import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from pytgcalls.types import StreamAudioQuality
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN, FORCE_SUB

# إعداد العميل
app = Client(
    "crystal_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# إعداد مشغل المكالمات (الإصدار 3.0.0+)
call = PyTgCalls(app)

ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
}

async def force_sub_check(client, message):
    if not FORCE_SUB: return True
    try:
        await client.get_chat_member(FORCE_SUB, message.from_user.id)
        return True
    except:
        await message.reply(
            "⚠️ **يجب عليك الاشتراك في القناة أولاً!**",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("اضغط للاشتراك", url=f"https://t.me/{FORCE_SUB}")]]
            )
        )
        return False

async def get_audio_data(query):
    search = VideosSearch(query, limit=1)
    results = search.result()["result"]
    if not results: return None, None
    link = results[0]["link"]
    title = results[0]["title"]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        return info["url"], title

@app.on_message(filters.command("start"))
async def start_cmd(_, message):
    await message.reply("✨ **Crystal Music Bot**\n\nأرسل `/play` مع اسم الأغنية.")

@app.on_message(filters.command("play") & filters.group)
async def play_cmd(client, message):
    if not await force_sub_check(client, message): return
    if len(message.command) < 2:
        return await message.reply("❌ اكتب اسم الأغنية.")

    query = " ".join(message.command[1:])
    m = await message.reply("🔎 جاري البحث...")

    try:
        audio_url, title = await get_audio_data(query)
        if not audio_url: return await m.edit("❌ لا توجد نتائج.")

        # التشغيل باستخدام الهيكلية الجديدة
        await call.join_group_call(
            message.chat.id,
            AudioPiped(audio_url, StreamAudioQuality.HIGH)
        )
        await m.edit(f"▶️ **تم التشغيل:**\n`{title}`")
    except Exception as e:
        await m.edit(f"❌ حدث خطأ: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop_cmd(_, message):
    try:
        await call.leave_group_call(message.chat.id)
        await message.reply("⏹ تم الإيقاف.")
    except:
        await message.reply("❌ البوت غير متصل.")

async def main():
    await app.start()
    await call.start()
    print("✅ Bot is running on Heroku!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
