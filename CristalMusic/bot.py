import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from pytgcalls.types.stream import StreamAudioQuality
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN, FORCE_SUB

app = Client(
    "crystal",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

call = PyTgCalls(app)

ydl_opts = {
    "format": "bestaudio",
    "quiet": True,
    "nocheckcertificate": True,
}

async def force_sub_check(client, message):
    try:
        user = await client.get_chat_member(FORCE_SUB, message.from_user.id)
        return True
    except:
        await message.reply(
            "⚠️ لازم تشترك بالقناة اولاً",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("اشترك", url=f"https://t.me/{FORCE_SUB}")]]
            )
        )
        return False

async def get_audio(query):
    search = VideosSearch(query, limit=1)
    result = search.result()["result"][0]["link"]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(result, download=False)
        return info["url"], info["title"]

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply(
        "✨ Crystal Music Bot\n\n"
        "الاوامر:\n"
        "/play اسم الاغنية"
    )

@app.on_message(filters.command("play") & filters.group)
async def play(_, message):
    if not await force_sub_check(app, message):
        return
    if len(message.command) < 2:
        return await message.reply("اكتب اسم الاغنية")

    query = " ".join(message.command[1:])
    m = await message.reply("🔎 جاري البحث...")
    
    try:
        audio, title = await get_audio(query)
        await call.join_group_call(
            message.chat.id,
            AudioPiped(audio, StreamAudioQuality.HIGH)
        )
        await m.edit(f"▶️ تم تشغيل:\n{title}")
    except Exception as e:
        await m.edit(f"❌ حدث خطأ: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop(_, message):
    try:
        await call.leave_group_call(message.chat.id)
        await message.reply("⏹ تم الايقاف")
    except:
        await message.reply("❌ البوت غير متصل بمكالمة")

async def main():
    await app.start()
    await call.start()
    print("Crystal Music Bot Started")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
