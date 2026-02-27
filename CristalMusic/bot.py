import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="CristalMusic",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
        )

    async def start(self):
        await super().start()
        print("✅ البوت اشتغل! جرب اكتب: تشغيل اسم الاغنية")

app = Bot()

# --- أمر التشغيل بدون / (تشغيل + اسم الاغنية) ---
@app.on_message(filters.text & filters.regex(r"^(تشغيل|شغل)\s+(.*)"))
async def play_by_text(client, message):
    # استخراج اسم الأغنية من الرسالة
    query = message.matches[0].group(2)
    
    await message.reply_text(
        f"**🔍 جاري البحث عن:** `{query}`\n\n**يتم الآن التحضير للتشغيل...** 🎵",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏸ إيقاف مؤقت", callback_data="pause"),
                InlineKeyboardButton("▶️ استئناف", callback_data="resume")
            ],
            [
                InlineKeyboardButton("⏹ إيقاف نهائي", callback_data="stop")
            ]
        ])
    )

# --- أمر الإيقاف بكلمة "ايقاف" بدون / ---
@app.on_message(filters.text & filters.regex(r"^(ايقاف|توقف)$"))
async def stop_by_text(client, message):
    await message.reply_text("**تم إيقاف الموسيقى بنجاح!** ❌")

# --- معالجة ضغطات الأزرار (Callback) ---
@app.on_callback_query()
async def handle_buttons(client, query):
    if query.data == "pause":
        await query.answer("تم الإيقاف المؤقت ⏸", show_alert=True)
    elif query.data == "resume":
        await query.answer("تم الاستئناف ▶️")
    elif query.data == "stop":
        await query.edit_message_text("**تم إنهاء الجلسة وإيقاف الموسيقى.**")

async def main():
    await app.start()
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
