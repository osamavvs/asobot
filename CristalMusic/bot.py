import asyncio
import pyrogram.errors
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from youtubesearchpython import VideosSearch
import json
from config import API_ID, API_HASH, BOT_TOKEN

# تعريف الكائنات
app = Client("CristalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# --- قسم الأوامر بنظام الأزرار الشفافة ---

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        f"**أهلاً بك يا {message.from_user.mention} في بوت كريستال!**\n\n"
        "استخدم الأزرار أدناه للتحكم أو اكتب (تشغيل + اسم الأغنية):",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("قناة السورس", url="https://t.me/YourChannel"),
                InlineKeyboardButton("المطور", url="https://t.me/YourUser")
            ],
            [
                InlineKeyboardButton("أضف البوت لمجموعتك", url=f"https://t.me/{app.me.username}?startgroup=true")
            ]
        ])
    )

@app.on_message(filters.text & filters.regex(r"^(تشغيل|شغل)\s+(.*)"))
async def play_audio(client, message):
    query = message.matches[0].group(2)
    m = await message.reply_text(f"🔍 جاري البحث عن: `{query}`...")
    
    try:
        # البحث باستخدام المكتبة المستقرة
        search = VideosSearch(query, limit=1)
        results = search.result()
        
        if not results['result']:
            return await m.edit("❌ لم يتم العثور على نتائج.")

        video_data = results['result'][0]
        url = video_data['link']
        title = video_data['title']

        # التشغيل في المكالمة
        await call_py.join_group_call(
            message.chat.id,
            MediaStream(url)
        )
        
        # الرد بأزرار التحكم الشفافة
        await m.edit(
            f"🎵 **بدأ التشغيل الآن**\n\n**🏷 العنوان:** {title}",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⏸ إيقاف مؤقت", callback_data="pause"),
                    InlineKeyboardButton("▶️ استئناف", callback_data="resume")
                ],
                [
                    InlineKeyboardButton("⏹ إيقاف نهائي", callback_data="stop_btn")
                ]
            ])
        )
        
    except Exception as e:
        await m.edit(f"❌ حدث خطأ: {e}")

@app.on_message(filters.text & filters.regex(r"^(ايقاف|توقف)$"))
async def stop_audio_cmd(client, message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply_text("**تم إيقاف التشغيل بنجاح!** ❌")
    except:
        await message.reply_text("❌ لا يوجد تشغيل نشط حالياً.")

# --- معالجة ضغطات الأزرار (Callback) ---
@app.on_callback_query()
async def handle_buttons(client, query):
    if query.data == "pause":
        await call_py.pause_stream(query.message.chat.id)
        await query.answer("تم الإيقاف المؤقت ⏸")
    elif query.data == "resume":
        await call_py.resume_stream(query.message.chat.id)
        await query.answer("تم الاستئناف ▶️")
    elif query.data == "stop_btn":
        await call_py.leave_group_call(query.message.chat.id)
        await query.edit_message_text("**تم إنهاء الجلسة وإيقاف الموسيقى.** ⏹")

# --- وظيفة التشغيل الرئيسية ---
async def main():
    await app.start()
    await call_py.start()
    print("🚀 البوت جاهز: الأزرار والبحث يعملان معاً!")
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
