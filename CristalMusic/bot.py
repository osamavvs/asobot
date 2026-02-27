import asyncio
import pyrogram.errors
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL
from config import API_ID, API_HASH, BOT_TOKEN

# تعريف الكائنات في النطاق العام (Global Scope) لضمان رؤيتها
app = Client("CristalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# إعدادات البحث المتقدمة لتجاوز حماية يوتيوب
ytdl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0", # يساعد في تجنب حظر الآي بي على هيروكو
    "nocheckcertificate": True,
}
ytdl = YoutubeDL(ytdl_opts)
# --- قسم الأوامر ---
@app.on_message(filters.text & filters.regex(r"^(تشغيل|شغل)\s+(.*)"))
async def play_audio(client, message):
    query = message.matches[0].group(2)
    m = await message.reply_text(f"🔍 جاري البحث عن: `{query}`...")
    try:
        info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        url = info['url']
        title = info['title']
        await call_py.join_group_call(message.chat.id, MediaStream(url))
        await m.edit(f"🎵 تم بدء التشغيل:\n**{title}**")
    except Exception as e:
        await m.edit(f"❌ حدث خطأ: {e}")

@app.on_message(filters.text & filters.regex(r"^(ايقاف|توقف)$"))
async def stop_audio(client, message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply_text("✅ تم إيقاف التشغيل.")
    except:
        await message.reply_text("❌ لا يوجد تشغيل حالياً.")

# --- وظيفة التشغيل الرئيسية ---
async def main():
    await app.start()
    await call_py.start()
    print("🚀 البوت والمحرك الصوتي جاهزان للعمل!")
    from pyrogram import idle
    await idle()
