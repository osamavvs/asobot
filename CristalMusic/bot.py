import asyncio
import pyrogram.errors
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_search import SearchVideos
import json
from config import API_ID, API_HASH, BOT_TOKEN

# تعريف الكائنات
app = Client("CristalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# --- قسم الأوامر ---
@app.on_message(filters.text & filters.regex(r"^(تشغيل|شغل)\s+(.*)"))
async def play_audio(client, message):
    query = message.matches[0].group(2)
    m = await message.reply_text(f"🔍 جاري البحث عن: `{query}`...")
    
    try:
        # البحث باستخدام yt-search لتجاوز قيود يوتيوب
        search = SearchVideos(query, offset=1, mode="json", max_results=1)
        results = json.loads(search.result())
        
        if not results.get("search_result"):
            return await m.edit("❌ لم يتم العثور على نتائج.")

        video_data = results["search_result"][0]
        url = video_data["link"]
        title = video_data["title"]

        # التشغيل في المكالمة
        await call_py.join_group_call(
            message.chat.id,
            MediaStream(url)
        )
        await m.edit(f"🎵 **تم بدء التشغيل بنجاح**\n\n**🏷 العنوان:** {title}")
        
    except Exception as e:
        await m.edit(f"❌ حدث خطأ: {e}")

@app.on_message(filters.text & filters.regex(r"^(ايقاف|توقف)$"))
async def stop_audio(client, message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply_text("✅ تم إيقاف التشغيل ومغادرة المكالمة.")
    except:
        await message.reply_text("❌ لا يوجد تشغيل نشط حالياً.")

# --- وظيفة التشغيل الرئيسية ---
async def main():
    await app.start()
    await call_py.start()
    print("🚀 البوت جاهز والعزف بدأ!")
    from pyrogram import idle
    await idle()
