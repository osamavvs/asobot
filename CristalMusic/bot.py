import asyncio
import pyrogram.errors
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN

# تعريف الكائنات الأساسية
app = Client("CristalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# --- رسالة الترحيب /start ---
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        f"**👋 أهلاً بك يا {message.from_user.mention}**\n\n"
        "**أنا بوت تشغيل الموسيقى في المكالمات الصوتية.**\n"
        "**للتشغيل أرسل: شغل + اسم الأغنية**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ أضفني لمجموعتك", url=f"https://t.me/{app.me.username}?startgroup=true")]
        ])
    )

# --- أمر التشغيل (شغل / تشغيل) ---
@app.on_message(filters.text & filters.regex(r"^(تشغيل|شغل)\s+(.*)"))
async def play_audio(client, message):
    query = message.matches[0].group(2)
    m = await message.reply_text(f"🔍 **جاري البحث عن:** `{query}`...")
    
    try:
        # البحث عن الفيديو وجلب البيانات
        search = VideosSearch(query, limit=1)
        results = search.result()
        
        if not results['result']:
            return await m.edit("❌ **لم يتم العثور على نتائج للبحث!**")

        video_data = results['result'][0]
        url = video_data['link']
        title = video_data['title']
        thumb = video_data['thumbnails'][0]['url']
        duration = video_data['duration']

        # الانضمام للمكالمة وتشغيل الصوت
        await call_py.join_group_call(message.chat.id, MediaStream(url))
        
        # حذف رسالة البحث وإرسال الكارت الأنيق مع الأزرار الشفافة
        await m.delete()
        await message.reply_photo(
            photo=thumb,
            caption=(
                "**🎧 تم بدء التشغيل بنجاح**\n\n"
                f"**📌 العنوان:** `{title}`\n"
                f"**⏳ المدة:** `{duration}`\n"
                f"**👤 طلب بواسطة:** {message.from_user.mention}\n\n"
                "**👇 استخدم الأزرار أدناه للتحكم**"
            ),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⏸ مؤقت", callback_data="pause"),
                    InlineKeyboardButton("▶️ استئناف", callback_data="resume")
                ],
                [
                    InlineKeyboardButton("⏹ إيقاف النهائي", callback_data="stop")
                ]
            ])
        )
        
    except Exception as e:
        await m.edit(f"❌ **حدث خطأ:** {e}")

# --- أمر الإيقاف النصي ---
@app.on_message(filters.text & filters.regex(r"^(ايقاف|توقف)$"))
async def stop_audio_cmd(client, message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply_text("**✅ تم إيقاف التشغيل بنجاح!**")
    except:
        await message.reply_text("❌ **لا يوجد تشغيل نشط حالياً.**")

# --- معالجة ضغطات الأزرار (Callback) ---
@app.on_callback_query()
async def handle_buttons(client, query):
    chat_id = query.message.chat.id
    if query.data == "pause":
        await call_py.pause_stream(chat_id)
        await query.answer("تم الإيقاف المؤقت ⏸")
    elif query.data == "resume":
        await call_py.resume_stream(chat_id)
        await query.answer("تم الاستئناف ▶️")
    elif query.data == "stop":
        await call_py.leave_group_call(chat_id)
        await query.message.delete()
        await query.answer("تم إنهاء التشغيل ⏹")

# --- وظيفة الإقلاع الرئيسية ---
async def main():
    await app.start()
    await call_py.start()
    print("🚀 Cristal Music Bot is Online!")
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
