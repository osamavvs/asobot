import asyncio
import pyrogram.errors

# حيلة برمجية لتجاوز خطأ الإصدارات
if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    pyrogram.errors.GroupcallForbidden = type("GroupcallForbidden", (Exception,), {})

from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL
from config import API_ID, API_HASH, BOT_TOKEN
# إعدادات البحث في يوتيوب
ytdl_opts = {"format": "bestaudio/best", "quiet": True}
ytdl = YoutubeDL(ytdl_opts)

@app.on_message(filters.text & filters.regex(r"^(تشغيل|شغل)\s+(.*)"))
async def play_audio(client, message):
    query = message.matches[0].group(2)
    m = await message.reply_text(f"🔍 جاري البحث عن: `{query}`...")
    
    try:
        # البحث في يوتيوب
        info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        url = info['url']
        title = info['title']
        
        # الانضمام للمكالمة وتشغيل الصوت باستخدام التحديث الجديد MediaStream
        await call_py.join_group_call(
            message.chat.id,
            MediaStream(url) # تم التغيير من AudioPiped إلى MediaStream
        )
        await m.edit(f"🎵 تم بدء التشغيل:\n**{title}**")
    except Exception as e:
        await m.edit(f"❌ حدث خطأ: {e}")

@app.on_message(filters.text & filters.regex(r"^(ايقاف|توقف)$"))
async def stop_audio(client, message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply_text("✅ تم إيقاف التشغيل ومغادرة المكالمة.")
    except:
        await message.reply_text("❌ لا يوجد تشغيل حالياً.")

async def main():
    await app.start()
    await call_py.start()
    print("🚀 البوت والمحرك الصوتي جاهزان بالنسخة المحدثة!")
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
