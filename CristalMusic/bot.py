import asyncio
import yt_dlp
import os
import json
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import UserNotParticipant
# بدلاً من الاستدعاء القديم، استخدم هذا:
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from pytgcalls.types import StreamAudioQuality # بدلاً من HighQualityAudio
from pytgcalls.types import MediaStream
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, OWNER_USER, CHANNEL_USER

# --- الإعدادات ---
START_IMG = "https://telegra.ph/file/07f43f11f568a91439d5b.jpg"

app = Client("CristalMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# قاعدة بيانات بسيطة
def get_stats():
    if not os.path.exists("stats.json"): return {"users": [], "groups": []}
    return json.load(open("stats.json", "r"))

# --- [ 1. رسالة /start الذكية ] ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    
    # واجهة المطور
    if user_id == OWNER_ID:
        stats = get_stats()
        await message.reply_photo(
            photo=START_IMG,
            caption=(f"⚡️ **أهلاً بك يا مطور السورس ( {message.from_user.first_name} )**\n\n"
                     f"📊 **إحصائيات البوت الحالية :**\n"
                     f"👤 **المستخدمين :** `{len(stats['users'])}`\n"
                     f"🏘 **المجموعات :** `{len(stats['groups'])}`\n\n"
                     f"يمكنك إدارة البوت بالكامل من خلال الأزرار أدناه ."),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 إذاعة عامة", callback_data="broadcast"), InlineKeyboardButton("🚫 المحظورين", callback_data="banned_list")],
                [InlineKeyboardButton("💎 قناة السورس", url=f"https://t.me/{CHANNEL_USER}"), InlineKeyboardButton("🛠 الإعدادات", callback_data="settings")],
                [InlineKeyboardButton("🔄 تحديث البيانات", callback_data="refresh_stats")]
            ])
        )
    # واجهة العضو
    else:
        await message.reply_photo(
            photo=START_IMG,
            caption=(f"👋 **أهلاً بك يا {message.from_user.mention} في بوت كرستال**\n\n"
                     f"أنا بوت تشغيل الموسيقى في المكالمات الصوتية بأحدث التقنيات.\n\n"
                     f"📌 **استخدم الأزرار أدناه لمعرفة الأوامر وكيفية تشغيلي :**"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎮 أوامر التشغيل", callback_data="user_cmds"), InlineKeyboardButton("📖 تعليمات", callback_data="user_info")],
                [InlineKeyboardButton("💎 سورس كرستال", url=f"https://t.me/{CHANNEL_USER}"), InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{OWNER_USER}")],
                [InlineKeyboardButton("➕ أضف البوت لمجموعتك", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")]
            ])
        )

# --- [ 2. معالج الأزرار التفاعلي (Callback) ] ---
@app.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    # --- أقسام العضو ---
    if query.data == "user_cmds":
        await query.edit_message_caption(
            caption="🕹 **أوامر تشغيل الموسيقى :**\n\n"
                    "• `شغل` + اسم الأغنية أو الرابط .\n"
                    "• `ايقاف` : لإنهاء المكالمة .\n"
                    "• `تخطي` : لتشغيل الأغنية التالية .\n"
                    "• `مؤقت` : لإيقاف الصوت مؤقتاً .\n"
                    "• `استئناف` : لمواصلة الصوت .",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="back_user")]])
        )
    elif query.data == "user_info":
        await query.edit_message_caption(
            caption="📖 **كيفية استخدام البوت :**\n\n"
                    "1️⃣ أضف البوت لمجموعتك أولاً .\n"
                    "2️⃣ ارفع البوت 'مشرف' بكل الصلاحيات .\n"
                    "3️⃣ افتح 'المحادثة المرئية' في المجموعة .\n"
                    "4️⃣ أرسل كلمة `شغل` مع اسم الأغنية .\n\n"
                    "✅ سيقوم البوت بالانضمام والتشغيل فوراً .",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="back_user")]])
        )
    elif query.data == "back_user":
        await query.edit_message_caption(
            caption="👋 أهلاً بك مجدداً في قائمة سورس كرستال الرئيسية .",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎮 أوامر التشغيل", callback_data="user_cmds"), InlineKeyboardButton("📖 تعليمات", callback_data="user_info")],
                [InlineKeyboardButton("➕ أضف البوت لمجموعتك", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")]
            ])
        )
    # --- أقسام المطور ---
    elif query.data == "refresh_stats":
        await query.answer("🔄 تم تحديث الإحصائيات")
        # هنا نعيد كود عرض لوحة المطور المذكور في البداية
    elif query.data == "broadcast":
        await query.answer("أرسل الرسالة (نص/صورة) ثم قم بالرد عليها بكلمة 'اذاعة'", show_alert=True)

# --- [ 3. نظام التشغيل (مطابق ليوكي) ] ---
@app.on_message(filters.regex(r"^(شغل|تشغيل)\s+(.*)"))
async def play_handler(client, message):
    # فحص الاشتراك الإجباري
    try:
        await client.get_chat_member(CHANNEL_USER, message.from_user.id)
    except UserNotParticipant:
        return await message.reply_text(f"⚠️ اشترك أولاً: @{CHANNEL_USER}")
    
    query = message.matches[0].group(2)
    m = await message.reply_text("🔎 **جاري البحث...**")
    
    try:
        search = VideosSearch(query, limit=1).result()['result'][0]
        ydl_opts = {"format": "bestaudio[ext=m4a]", "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            audio_url = ydl.extract_info(search['link'], download=False)['url']
        
        await call_py.join_group_call(message.chat.id, MediaStream(audio_url))
        await m.delete()
        await message.reply_photo(
            photo=search['thumbnails'][0]['url'],
            caption=f"✅ **بدأ التشغيل الآن**\n\n**📌 العنوان:** `{search['title']}`\n**👤 المطور:** @{OWNER_USER}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إغلاق ⏹", callback_data="stop")]])
        )
    except Exception as e:
        await m.edit(f"❌ خطأ: {e}")

async def main():
    await app.start()
    await call_py.start()
    print("💎 Cristal (Yuki Clone) is Online!")
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
