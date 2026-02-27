import asyncio
import yt_dlp
import json
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN

# --- الإعدادات ---
OWNER_ID = 8074717568 
OWNER_USER = "U_K44"
CHANNEL_USER = "BBABB9"
START_IMG = "https://telegra.ph/file/07f43f11f568a91439d5b.jpg"

app = Client("CristalMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# --- نظام الاشتراك الإجباري ---
async def check_subscribe(client, message):
    try:
        await client.get_chat_member(CHANNEL_USER, message.from_user.id)
    except UserNotParticipant:
        await message.reply_text(
            f"⚠️ **عذراً عزيزي، عليك الاشتراك في قناة البوت أولاً لاستخدام ميزاته.**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إضغط هنا للاشتراك 📢", url=f"https://t.me/{CHANNEL_USER}")]])
        )
        return False
    except: return True
    return True

# --- [1] أوامر المجموعات (أزرار شفافة وروابط) ---

@app.on_message(filters.regex("^الاوامر$") & filters.group)
async def group_cmds(client, message):
    await message.reply_text(
        "🎭 **قائمة التحكم في التشغيل:**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⏸ مؤقت", callback_data="pause"), InlineKeyboardButton("▶️ استئناف", callback_data="resume")],
            [InlineKeyboardButton("⏭ تخطي", callback_data="skip"), InlineKeyboardButton("⏹ إيقاف", callback_data="stop")],
            [InlineKeyboardButton("قناة السورس ⚡️", url=f"https://t.me/{CHANNEL_USER}")]
        ])
    )

@app.on_message(filters.regex("^المطور$") & filters.group)
async def group_dev(client, message):
    await message.reply_text(
        "👤 **معلومات مطور البوت:**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("تواصل مع المطور 👨‍💻", url=f"https://t.me/{OWNER_USER}")]])
    )

@app.on_message(filters.regex("^السورس$") & filters.group)
async def group_source(client, message):
    await message.reply_text(
        "💎 **سورس كرستال ميوزك:**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("قناة السورس 📢", url=f"https://t.me/{CHANNEL_USER}")],
            [InlineKeyboardButton("مطور السورس 👤", url=f"https://t.me/{OWNER_USER}")]
        ])
    )

# --- [2] واجهة الخاص (دليل مستخدم كامل) ---

@app.on_message(filters.command("start") & filters.private)
async def start_private(client, message):
    if not await check_subscribe(client, message): return
    await message.reply_photo(
        photo=START_IMG,
        caption=(f"👋 **أهلاً بك {message.from_user.mention} في بوت كرستال**\n\n"
                 f"أنا بوت تشغيل الموسيقى في المكالمات الصوتية بجودة عالية.\n\n"
                 f"📌 **يمكنك التحكم من خلال الأزرار أدناه:**"),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("كيفية التشغيل 📖", callback_data="help_how"), InlineKeyboardButton("الأوامر 🕹", callback_data="help_cmds")],
            [InlineKeyboardButton("السورس والقناة 💎", callback_data="help_source")],
            [InlineKeyboardButton("إضافة البوت للمجموعة ➕", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")],
            [InlineKeyboardButton("تواصل مع المطور 👨‍💻", url=f"https://t.me/{OWNER_USER}")]
        ])
    )

@app.on_callback_query()
async def private_buttons(client, query):
    if query.data == "help_how":
        await query.edit_message_caption(
            caption="💡 **كيفية تشغيل البوت في مجموعتك:**\n\n"
                    "1️⃣ أضف البوت لمجموعتك أولاً.\n"
                    "2️⃣ ارفع البوت 'مشرف' بكل الصلاحيات.\n"
                    "3️⃣ افتح 'المحادثة المرئية' (Video Chat).\n"
                    "4️⃣ أرسل كلمة `شغل` + اسم الأغنية.\n\n"
                    "✅ سيقوم البوت بالانضمام والتشغيل تلقائياً.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="back_home")]])
        )
    elif query.data == "help_cmds":
        await query.edit_message_caption(
            caption="🕹 **أوامر التحكم بالبوت:**\n\n"
                    "• `شغل` + اسم الأغنية أو الرابط.\n"
                    "• `ايقاف` : لإنهاء التشغيل تماماً.\n"
                    "• `مؤقت` : لإيقاف التشغيل مؤقتاً.\n"
                    "• `استئناف` : لمواصلة التشغيل.\n"
                    "• `تخطي` : لتشغيل الأغنية التالية في الطابور.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="back_home")]])
        )
    elif query.data == "help_source":
        await query.edit_message_caption(
            caption=f"💎 **معلومات سورس كرستال:**\n\n"
                    f"📢 **قناتنا:** @{CHANNEL_USER}\n"
                    f"👤 **المطور:** @{OWNER_USER}\n\n"
                    f"شكراً لاستخدامك سورس كرستال المتطور.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="back_home")]])
        )
    elif query.data == "back_home":
        await query.edit_message_caption(
            caption="👋 أهلاً بك مجدداً في قائمة التحكم الرئيسية.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("كيفية التشغيل 📖", callback_data="help_how"), InlineKeyboardButton("الأوامر 🕹", callback_data="help_cmds")],
                [InlineKeyboardButton("السورس والقناة 💎", callback_data="help_source")],
                [InlineKeyboardButton("إضافة البوت للمجموعة ➕", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")]
            ])
        )
    # أكواد التشغيل السابقة (ايقاف، مؤقت الخ)
    elif query.data == "stop":
        await call_py.leave_group_call(query.message.chat.id)
        await query.answer("تم الإيقاف")

# --- نظام التشغيل المستقر ---
@app.on_message(filters.text & filters.regex(r"^(شغل|تشغيل)\s+(.*)"))
async def play_handler(client, message):
    if not await check_subscribe(client, message): return
    query = message.matches[0].group(2)
    m = await message.reply_text("🔎 **جاري البحث والتحضير...**")
    try:
        search = VideosSearch(query, limit=1).result()['result'][0]
        with yt_dlp.YoutubeDL({"format": "bestaudio[ext=m4a]", "quiet": True}) as ydl:
            audio_url = ydl.extract_info(search['link'], download=False)['url']
        await call_py.join_group_call(message.chat.id, MediaStream(audio_url))
        await m.delete()
        await message.reply_photo(photo=search['thumbnails'][0]['url'], caption=f"✅ **بدأ التشغيل الآن:**\n`{search['title']}`")
    except Exception as e: await m.edit(f"❌ خطأ: {e}")

async def main():
    await app.start()
    await call_py.start()
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
