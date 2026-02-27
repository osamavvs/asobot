import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN

# تعريف الكائنات
app = Client("CristalMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# --- وظيفة الانضمام التلقائي للمساعد ---
async def join_assistant(client, chat_id):
    try:
        # محاولة الحصول على معلومات الدردشة للتأكد من وجود المساعد
        await client.get_chat_member(chat_id, "me")
    except Exception:
        try:
            # إذا لم يكن موجوداً، يحاول البوت صنع رابط دعوة أو الانضمام مباشرة
            link = await app.export_chat_invite_link(chat_id)
            await client.join_chat(link)
            print(f"✅ انضم المساعد للمجموعة: {chat_id}")
        except Exception as e:
            print(f"❌ فشل انضمام المساعد: {e}")
            return False
    return True

# --- أمر التشغيل مع استدعاء المساعد ---
@app.on_message(filters.text & filters.regex(r"^(تشغيل|شغل)\s+(.*)"))
async def play_audio(client, message):
    query = message.matches[0].group(2)
    chat_id = message.chat.id
    m = await message.reply_text("🔎 **جاري فحص المساعد والبحث...**")
    
    # محاولة إدخال المساعد تلقائياً
    await join_assistant(client, chat_id)

    try:
        search = VideosSearch(query, limit=1)
        results = search.result()
        if not results['result']:
            return await m.edit("❌ **لم أجد نتائج!**")

        video = results['result'][0]
        url = video['link']
        title = video['title']
        thumb = video['thumbnails'][0]['url']

        # الانضمام للمكالمة وتشغيل الصوت
        try:
            await call_py.join_group_call(chat_id, MediaStream(url))
        except Exception as e:
            return await m.edit(f"❌ **تأكد من فتح المكالمة الصوتية أولاً!**\nالخطأ: {e}")

        await m.delete()
        await message.reply_photo(
            photo=thumb,
            caption=(
                f"**🎵 تم بدء التشغيل بنجاح**\n\n"
                f"**📌 العنوان:** `{title}`\n"
                f"**👤 بواسطة:** {message.from_user.mention}"
            ),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⏸ مؤقت", callback_data="pause"),
                    InlineKeyboardButton("▶️ استمرار", callback_data="resume")
                ],
                [InlineKeyboardButton("⏹ إيقاف النهائي", callback_data="stop")]
            ])
        )
    except Exception as e:
        await m.edit(f"❌ **حدث خطأ:** {e}")

# --- معالجة الأزرار ---
@app.on_callback_query()
async def callbacks(client, query):
    if query.data == "pause":
        await call_py.pause_stream(query.message.chat.id)
        await query.answer("تم الإيقاف المؤقت")
    elif query.data == "resume":
        await call_py.resume_stream(query.message.chat.id)
        await query.answer("تم الاستئناف")
    elif query.data == "stop":
        await call_py.leave_group_call(query.message.chat.id)
        await query.message.delete()

async def main():
    await app.start()
    await call_py.start()
    print("🚀 البوت والمساعد جاهزان مع ميزة الانضمام التلقائي!")
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
