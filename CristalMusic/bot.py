import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN

# تعريف الكائنات
app = Client("CristalMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# نظام الطابور (Queue) لتخزين الأغاني القادمة
queue = {}

def add_to_queue(chat_id, title, url, duration, user):
    if chat_id not in queue:
        queue[chat_id] = []
    queue[chat_id].append({"title": title, "url": url, "duration": duration, "user": user})

# --- وظيفة الانضمام التلقائي (مثل يوكي) ---
async def join_assistant(chat_id):
    try:
        await app.get_chat_member(chat_id, "me")
    except:
        try:
            link = await app.export_chat_invite_link(chat_id)
            # هنا نفترض أن المساعد يعمل بنفس الـ Client أو عبر Session String
            # في بوت يوكي، المساعد ينضم عبر الرابط فوراً
            print(f"✅ المساعد يحاول الانضمام للمجموعة {chat_id}")
        except:
            pass

# --- أمر التشغيل المتطور ---
@app.on_message(filters.text & filters.regex(r"^(شغل|تشغيل)\s+(.*)"))
async def play_handler(client, message):
    query = message.matches[0].group(2)
    chat_id = message.chat.id
    m = await message.reply_text("✨ **جاري المعالجة...**")
    
    await join_assistant(chat_id)

    try:
        search = VideosSearch(query, limit=1)
        result = search.result()['result'][0]
        
        title = result['title']
        url = result['link']
        duration = result['duration']
        thumb = result['thumbnails'][0]['url']
        user = message.from_user.mention

        # إذا كان هناك تشغيل حالي، أضف للطابور
        if chat_id in queue and len(queue[chat_id]) > 0:
            add_to_queue(chat_id, title, url, duration, user)
            return await m.edit(f"📝 **تمت الإضافة للطابور:**\n**{title}**")

        # بدء التشغيل فوراً
        await call_py.join_group_call(chat_id, MediaStream(url))
        add_to_queue(chat_id, title, url, duration, user)

        await m.delete()
        await message.reply_photo(
            photo=thumb,
            caption=(
                f"**🎸 بدأ التشغيل الآن (نسخة يوكي)**\n\n"
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
        await m.edit(f"❌ خطأ: {e}")

# --- التحكم (الأزرار) ---
@app.on_callback_query()
async def controls(client, query):
    chat_id = query.message.chat.id
    if query.data == "pause":
        await call_py.pause_stream(chat_id)
        await query.answer("تم الإيقاف المؤقت")
    elif query.data == "resume":
        await call_py.resume_stream(chat_id)
        await query.answer("تم الاستئناف")
    elif query.data == "stop":
        if chat_id in queue:
            queue[chat_id] = []
        await call_py.leave_group_call(chat_id)
        await query.message.delete()
    elif query.data == "skip":
        await query.answer("جاري تخطي الأغنية...")
        # هنا يمكن إضافة منطق السحب من الطابور (Next)
        await call_py.leave_group_call(chat_id)

async def main():
    await app.start()
    await call_py.start()
    print("💎 Cristal (Yuki Clone) is ready!")
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
