import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN

# 1. تعريف الكائنات (نفس إعداداتك القديمة)
app = Client("CristalMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# 2. نظام الطابور (Queue) - للحفاظ على ترتيب الأغاني
queue = {}

def add_to_queue(chat_id, title, url, duration, user):
    if chat_id not in queue:
        queue[chat_id] = []
    queue[chat_id].append({"title": title, "url": url, "duration": duration, "user": user})

# 3. إعدادات المستخرج المستقر (لتجاوز حظر يوتيوب)
YDL_OPTIONS = {
    "format": "bestaudio[ext=m4a]",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# 4. وظيفة الانضمام التلقائي للمساعد (التي طلبتها سابقاً)
async def join_assistant(chat_id):
    try:
        await app.get_chat_member(chat_id, "me")
    except:
        try:
            # محاولة تصدير رابط دعوة للمساعد
            link = await app.export_chat_invite_link(chat_id)
            print(f"✅ محاولة انضمام المساعد للمجموعة {chat_id}")
        except:
            pass

# 5. أمر التشغيل المتطور (يجمع بين الاستقرار والطابور)
@app.on_message(filters.text & filters.regex(r"^(شغل|تشغيل)\s+(.*)"))
async def play_handler(client, message):
    query = message.matches[0].group(2)
    chat_id = message.chat.id
    m = await message.reply_text("🔎 **جاري المعالجة والاستخراج المستقر...**")
    
    # استدعاء المساعد تلقائياً
    await join_assistant(chat_id)

    try:
        # البحث عن الفيديو
        search = VideosSearch(query, limit=1)
        result = search.result()['result'][0]
        
        title = result['title']
        video_url = result['link']
        duration = result['duration']
        thumb = result['thumbnails'][0]['url']
        user = message.from_user.mention

        # استخراج رابط الصوت المباشر (حل مشكلة عدم التشغيل)
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(video_url, download=False)
                audio_url = info['url']
        except Exception as e:
            return await m.edit(f"❌ **فشل تجاوز حماية يوتيوب:**\n`{e}`")

        # إدارة الطابور (إذا كان هناك شيء يعمل، أضف للقائمة)
        if chat_id in queue and len(queue[chat_id]) > 0:
            add_to_queue(chat_id, title, audio_url, duration, user)
            return await m.edit(f"📝 **تمت الإضافة للطابور:**\n**{title}**")

        # تشغيل الصوت في المكالمة
        try:
            await call_py.join_group_call(chat_id, MediaStream(audio_url))
            add_to_queue(chat_id, title, audio_url, duration, user)
        except Exception as e:
            return await m.edit(f"❌ **فشل في المكالمة:**\nتأكد من فتح المحادثة المرئية!\n`{e}`")

        await m.delete()
        await message.reply_photo(
            photo=thumb,
            caption=(
                f"**🎸 بدأ التشغيل الآن (نسخة يوكي المستقرة)**\n\n"
                f"**📌 العنوان:** `{title}`\n"
                f"**⏳ المدة:** `{duration}`\n"
                f"**👤 بواسطة:** {user}\n"
            ),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⏸", callback_data="pause"),
                    InlineKeyboardButton("▶️", callback_data="resume"),
                    InlineKeyboardButton("⏭", callback_data="skip")
                ],
                [InlineKeyboardButton("⏹ إيقاف نهائي", callback_data="stop")]
            ])
        )
    except Exception as e:
        await m.edit(f"❌ **خطأ غير متوقع:**\n`{e}`")

# 6. التحكم بالأزرار (نفس إعداداتك القديمة مع تحسين التخطي)
@app.on_callback_query()
async def controls(client, query):
    chat_id = query.message.chat.id
    if query.data == "pause":
        await call_py.pause_stream(chat_id)
        await query.answer("تم الإيقاف المؤقت ⏸")
    elif query.data == "resume":
        await call_py.resume_stream(chat_id)
        await query.answer("تم الاستئناف ▶️")
    elif query.data == "stop":
        if chat_id in queue:
            queue[chat_id] = []
        await call_py.leave_group_call(chat_id)
        await query.message.delete()
        await query.answer("تم الإيقاف النهائي ⏹")
    elif query.data == "skip":
        if chat_id in queue and len(queue[chat_id]) > 1:
            queue[chat_id].pop(0)
            next_track = queue[chat_id][0]
            await call_py.change_stream(chat_id, MediaStream(next_track['url']))
            await query.answer("تم التخطي ⏭")
            await query.edit_message_caption(caption=f"⏭ **تم التخطي إلى:**\n`{next_track['title']}`")
        else:
            await call_py.leave_group_call(chat_id)
            await query.message.delete()
            await query.answer("انتهى الطابور!")

# 7. تشغيل البوت
async def main():
    await app.start()
    await call_py.start()
    print("💎 Cristal (Stable Yuki) is Online!")
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
