import asyncio
import yt_dlp
from pyrogram import filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from youtubesearchpython import VideosSearch

from core.client import app, call_py
from config import OWNER_ID, OWNER_USER, CHANNEL_USER

# استيراد الميديا المتوافق
try:
    from pytgcalls.types import MediaStream
except:
    from pytgcalls.types.input_stream import MediaStream

START_IMG = "https://telegra.ph/file/07f43f11f568a91439d5b.jpg"

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_photo(
        photo=START_IMG,
        caption=f"👋 أهلاً بك {message.from_user.mention}\nفي سورس كرستال ميوزك الجديد.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎮 الأوامر", callback_data="cmds")]])
    )

@app.on_message(filters.regex(r"^(شغل|تشغيل)\s+(.*)"))
async def play(client, message):
    query = message.matches[0].group(2)
    m = await message.reply_text("🔎 جاري البحث...")
    try:
        search = VideosSearch(query, limit=1).result()['result'][0]
        ydl_opts = {"format": "bestaudio[ext=m4a]", "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            audio_url = ydl.extract_info(search['link'], download=False)['url']
        
        await call_py.join_group_call(message.chat.id, MediaStream(audio_url))
        await m.edit(f"✅ تم التشغيل: **{search['title']}**")
    except Exception as e:
        await m.edit(f"❌ حدث خطأ: {e}")

async def main():
    await app.start()
    await call_py.start()
    print("💎 Cristal Music is Online!")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
