import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN

# تعريف الكائنات
app = Client("CristalMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# نظام الطابور (Queue)
queue = {}

def add_to_queue(chat_id, title, url, duration, user):
    if chat_id not in queue:
        queue[chat_id] = []
    queue[chat_id].append({"title": title, "url": url, "duration": duration, "user": user})

# --- صائد أخطاء الانضمام ---
async def join_assistant(chat_id):
    try:
        await app.get_chat_member(chat_id, "me")
    except Exception as e:
        print(f"⚠️ تنبيه صائد الأخطاء: المساعد غير موجود أو لا يملك صلاحيات. الخطأ: {e}")

# --- أمر التشغيل المدمج مع صائد الأخطاء ---
@app.on_message(filters.text & filters.regex(r"^(شغل|تشغيل)\s+(.*)"))
async def play_handler(client, message):
    query = message.matches[0].group(2)
    chat_id = message.chat.id
    m = await message.reply_text("✨ **جاري الفحص والتحضير...**")
    
    await join_assistant(chat_id)

    try:
        # 🛡️ صائد أخطاء 1: البحث
        try:
            search = VideosSearch(query, limit=1)
            result = search.result()['result'][0]
            title = result['title']
            video_url = result['link']
            duration = result['duration']
            thumb = result['thumbnails'][0]['url']
            user = message.from_user.mention
        except Exception as e:
            return await m.edit(f"❌ **صائد الأخطاء [البحث]:**\nلم أتمكن من العثور على نتائج. \nالسبب: `{e}`")

        # 🛡️ صائد أخطاء 2: استخراج الرابط المباشر
        try:
            ydl_opts = {"format": "bestaudio[ext=m4a]"}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                audio_url = info['url']
        except Exception as e:
            return await m.edit(f"❌ **صائد الأخطاء [الاستخراج]:**\nفشل استخراج رابط الصوت الخام.\nالسبب: `{e}`")

        # إدارة الطابور
        if chat_id in queue and len(queue[chat_id]) > 0:
            add_to_queue(chat_id, title, audio_url, duration, user)
            return await m.edit(f"📝 **تمت الإضافة للطابور:**\n**{title}**")

        # 🛡️ صائد أخطاء 3: الانضمام للمكالمة
        try:
            await call_py.join_group_call(chat_id, MediaStream(audio_url))
            add_to_queue(chat_id, title, audio_url, duration, user)
        except Exception as e:
            return await m.edit(f"❌ **صائد الأخطاء [المكالمة]:**\nفشل المساعد في الانضمام للمكالمة.\nالسبب: `{e}`\n\n*تأكد من فتح المكالمة يدوياً أولاً!*")

        await m.delete()
        await message.reply_photo(
            photo=thumb,
            caption=(
                f"**🎸 بدأ التشغيل الآن (نسخة يوكي المدمجة)**\n\n"
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

# --- التحكم بالأزرار ---
@app.on_callback_query()
async def controls(client, query):
    chat_id = query.message.chat.id
    try:
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
        elif query.data == "skip":
            if chat_id in queue and len(queue[chat_id]) > 1:
                queue[chat_id].pop(0)
                next_track = queue[chat_id][0]
                await call_py.change_stream(chat_id, MediaStream(next_track['url']))
                await query.answer("تم تخطي الأغنية ⏭")
                await query.edit_message_caption(caption=f"⏭ **تم التخطي إلى:**\n{next_track['title']}")
            else:
                await call_py.leave_group_call(chat_id)
                await query.message.delete()
                await query.answer("انتهى الطابور!")
    except Exception as e:
        await query.answer(f"❌ خطأ في التحكم: {e}", show_alert=True)

async def main():
    await app.start()
    await call_py.start()
    print("🚀 Cristal (Error-Capture) Mode Online!")
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
