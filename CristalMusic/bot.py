import asyncio
import yt_dlp
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import UserNotParticipant
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN

# --- الإعدادات (تأكد من وضع معلوماتك في config.py) ---
OWNER_ID = 8074717568 
OWNER_USER = "U_K44"
CHANNEL_USER = "BBABB9"
START_IMG = "https://telegra.ph/file/07f43f11f568a91439d5b.jpg"

app = Client("CristalMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# --- نظام الاشتراك الإجباري (يوكي ستايل) ---
async def check_sub(client, message):
    try:
        await client.get_chat_member(CHANNEL_USER, message.from_user.id)
    except UserNotParticipant:
        await message.reply_text(
            f"👋 **عزيزي {message.from_user.mention}**\n\n**يجب عليك الاشتراك في قناة السورس أولاً لاستخدام البوت.**\n\n**قناتنا:** @{CHANNEL_USER}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("اضغط هنا للاشتراك 💎", url=f"https://t.me/{CHANNEL_USER}")]])
        )
        return False
    except: return True
    return True

# --- [ 1. القائمة الرئيسية الاحترافية ] ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    if not await check_sub(client, message): return
    await message.reply_photo(
        photo=START_IMG,
        caption=(f"✨ **أهلاً بك في سورس كرستال الموسيقي**\n\n"
                 f"أنا بوت تشغيل الأغاني في المكالمات الصوتية بأحدث التقنيات وبدون انقطاع .\n\n"
                 f"👤 **المطور:** @{OWNER_USER}\n"
                 f"📢 **القناة:** @{CHANNEL_USER}\n\n"
                 f"**اضغط على الأزرار أدناه لاستكشاف الأوامر 👇**"),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 أوامر التشغيل", callback_data="cmds"), InlineKeyboardButton("🕹 أوامر التحكم", callback_data="ctrl")],
            [InlineKeyboardButton("💎 سورس كرستال", callback_data="source"), InlineKeyboardButton("👨‍💻 المطور", callback_data="dev")],
            [InlineKeyboardButton("➕ أضف البوت لمجموعتك", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")]
        ])
    )

# --- [ 2. معالج الأوامر المتداخل (Callback) ] ---
@app.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    if query.data == "cmds":
        await query.edit_message_caption(
            caption="🎮 **أوامر التشغيل (نسخة يوكي) :**\n\n"
                    "• `شغل` + اسم الأغنية أو الرابط .\n"
                    "• `تشغيل` + اسم الأغنية أو الرابط .\n"
                    "• `بحث` + اسم الأغنية (للحصول على روابط) .\n\n"
                    "💡 **ملاحظة:** يمكنك الرد على أي رابط أو ملف صوتي بكلمة `شغل` ليتم تشغيله فوراً .",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="home")]])
        )
    elif query.data == "ctrl":
        await query.edit_message_caption(
            caption="🕹 **أزرار التحكم السريع :**\n\n"
                    "• `ايقاف` : لإنهاء المكالمة .\n"
                    "• `تخطي` : لتشغيل الأغنية التالية .\n"
                    "• `مؤقت` : لإيقاف الصوت مؤقتاً .\n"
                    "• `استئناف` : لمواصلة الصوت .",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏮", callback_data="skip"), InlineKeyboardButton("⏸", callback_data="pause"), InlineKeyboardButton("▶️", callback_data="resume"), InlineKeyboardButton("⏹", callback_data="stop")],
                [InlineKeyboardButton("⬅️ رجوع", callback_data="home")]
            ])
        )
    elif query.data == "dev":
        await query.edit_message_caption(
            caption=(f"👤 **معلومات المطور الأساسي :**\n\n"
                     f"**• الاسم:** {OWNER_USER}\n"
                     f"**• المعرف:** @{OWNER_USER}\n"
                     f"**• الحساب:** [اضغط هنا](https://t.me/{OWNER_USER})\n\n"
                     f"أنا هنا لمساعدتك في حال واجهت أي مشكلة ."),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("تواصل مع المطور 👨‍💻", url=f"https://t.me/{OWNER_USER}")], [InlineKeyboardButton("⬅️ رجوع", callback_data="home")]])
        )
    elif query.data == "source":
        await query.edit_message_caption(
            caption=f"💎 **حول سورس كرستال :**\n\n"
                    f"أقوى سورس برمجيات ميوزك في التليجرام .\n"
                    f"يتميز بالسرعة الفائقة وجودة الصوت النقية .\n\n"
                    f"📢 القناة: @{CHANNEL_USER}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("قناة السورس ⚡️", url=f"https://t.me/{CHANNEL_USER}")], [InlineKeyboardButton("⬅️ رجوع", callback_data="home")]])
        )
    elif query.data == "home":
        await query.edit_message_caption(
            caption="✨ أهلاً بك مجدداً في قائمة سورس كرستال الرئيسية .",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 أوامر التشغيل", callback_data="cmds"), InlineKeyboardButton("🕹 أوامر التحكم", callback_data="ctrl")],
                [InlineKeyboardButton("💎 سورس كرستال", callback_data="source"), InlineKeyboardButton("👨‍💻 المطور", callback_data="dev")],
                [InlineKeyboardButton("➕ أضف البوت لمجموعتك", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")]
            ])
        )
    # أوامر التحكم الحقيقية (الخلفية)
    elif query.data == "stop":
        try: await call_py.leave_group_call(query.message.chat.id)
        except: pass
        await query.answer("تم الإيقاف نهائياً ⏹")

# --- [ 3. نظام التشغيل (الاحترافي) ] ---
@app.on_message(filters.regex(r"^(شغل|تشغيل)\s+(.*)") | (filters.regex(r"^(شغل|تشغيل)$") & filters.reply))
async def play_handler(client, message):
    if not await check_sub(client, message): return
    
    m = await message.reply_text("🔎 **جاري البحث والتحضير...**")
    
    # جلب النص سواء كان بحث أو رد
    query = message.matches[0].group(2) if not message.reply_to_message else message.reply_to_message.text
    
    try:
        search = VideosSearch(query, limit=1).result()['result'][0]
        title, link, thumb = search['title'], search['link'], search['thumbnails'][0]['url']
        
        ydl_opts = {"format": "bestaudio[ext=m4a]", "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            audio_url = info['url']

        await call_py.join_group_call(message.chat.id, MediaStream(audio_url))
        await m.delete()
        await message.reply_photo(
            photo=thumb,
            caption=f"✅ **بدأ التشغيل الآن بنجاح**\n\n**📌 العنوان:** `{title}`\n**👤 المطور:** @{OWNER_USER}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إغلاق المكالمة ⏹", callback_data="stop")]])
        )
    except Exception as e:
        await m.edit(f"❌ **حدث خطأ أثناء التشغيل :**\n`{e}`")

# --- [ 4. أوامر المجموعات السريعة ] ---
@app.on_message(filters.regex("^الاوامر$") & filters.group)
async def group_cmds(client, message):
    await message.reply_text("🎭 **تفضل أوامر التشغيل عزيزي :**", 
    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("أوامر التشغيل 🎮", callback_data="cmds")]]))

@app.on_message(filters.regex("^المطور$"))
async def dev_msg(client, message):
    await dev_info_logic(client, message) # استدعاء منطق المطور

async def main():
    await app.start()
    await call_py.start()
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
