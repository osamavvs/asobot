import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped # تحسين الاستيراد
from pytgcalls.types.stream import StreamAudioQuality # الجودة الحديثة
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN, FORCE_SUB

app = Client(
    "crystal",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

call = PyTgCalls(app)

# إعدادات البحث والتحميل
ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
}

# تحسين دالة التحقق من الاشتراك
async def force_sub_check(client, message):
    if not FORCE_SUB:
        return True
    try:
        await client.get_chat_member(FORCE_SUB, message.from_user.id)
        return True
    except Exception:
        await message.reply(
            "⚠️ **عذراً، يجب عليك الاشتراك في القناة أولاً لاستخدام البوت.**",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("اضغط هنا للاشتراك", url=f"https://t.me/{FORCE_SUB}")]]
            )
        )
        return False

# تحسين دالة جلب الصوت
async def get_audio(query):
    search = VideosSearch(query, limit=1)
    result_list = search.result()["result"]
    if not result_list:
        return None, None
    
    result_url = result_list[0]["link"]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(result_url, download=False)
        return info["url"], info["title"]

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply(
        "✨ **Crystal Music Bot**\n\n"
        "أهلاً بك! أنا بوت تشغيل الموسيقى في المكالمات.\n\n"
        "**الاوامر:**\n"
        "• `/play` + اسم الاغنية\n"
        "• `/stop` لإيقاف التشغيل"
    )

@app.on_message(filters.command("play") & filters.group)
async def play(_, message):
    if not await force_sub_check(app, message):
        return

    if len(message.command) < 2:
        return await message.reply("❌ **يرجى كتابة اسم الاغنية!**")

    query = " ".join(message.command[1:])
    m = await message.reply("🔎 **جاري البحث...**")

    try:
        audio, title = await get_audio(query)
        if not audio:
            return await m.edit("❌ **لم يتم العثور على نتائج.**")

        # الانضمام والتشغيل
        await call.join_group_call(
            message.chat.id,
            AudioPiped(audio, StreamAudioQuality.HIGH)
        )
        await m.edit(f"▶️ **تم التشغيل بنجاح:**\n\n**🎵:** `{title}`")
    except Exception as e:
        await m.edit(f"❌ **حدث خطأ غير متوقع:**\n`{str(e)}`")

@app.on_message(filters.command("stop") & filters.group)
async def stop(_, message):
    try:
        await call.leave_group_call(message.chat.id)
        await message.reply("⏹ **تم الإيقاف بنجاح.**")
    except:
        await message.reply("❌ **البوت غير متصل بمكالمة حالياً.**")

async def main():
    await app.start()
    await call.start()
    print("✅ Crystal Music Bot Started Successfully")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
