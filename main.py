import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from pytgcalls.types.stream import StreamAudioQuality
from youtubesearchpython import VideosSearch
import yt_dlp
from config import API_ID, API_HASH, BOT_TOKEN

app = Client("CrystalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

@app.on_message(filters.command("play") & filters.group)
async def play(_, message):
    if len(message.command) < 2:
        return await message.reply("❌ ارسل اسم الأغنية")
    
    m = await message.reply("🔎 جاري البحث...")
    query = " ".join(message.command[1:])
    
    try:
        search = VideosSearch(query, limit=1).result()["result"][0]
        link = search["link"]
        with yt_dlp.YoutubeDL({"format": "bestaudio", "quiet": True}) as ydl:
            info = ydl.extract_info(link, download=False)
            url = info["url"]
            
        await call.join_group_call(
            message.chat.id,
            AudioPiped(url, StreamAudioQuality.HIGH)
        )
        await m.edit(f"▶️ تم التشغيل: {search['title']}")
    except Exception as e:
        await m.edit(f"❌ خطأ: {e}")

async def start():
    await app.start()
    await call.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start())
