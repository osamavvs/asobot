import asyncio
import yt_dlp
import json
import os
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN

# --- الإعدادات الأساسية ---
OWNER_ID = 8074717568 
OWNER_USER = "U_K44"
CHANNEL_USER = "BBABB9"
START_IMG = "https://telegra.ph/file/07f43f11f568a91439d5b.jpg"

app = Client("CristalMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# --- نظام قواعد البيانات البسيط ---
STATS_FILE = "stats.json"
BANNED_FILE = "banned.json"

def load_data(file, default):
    if not os.path.exists(file): return default
    with open(file, "r") as f:
        try: return json.load(f)
        except: return default

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f)

stats = load_data(STATS_FILE, {"users": [], "groups": []})
banned_users = load_data(BANNED_FILE, [])

# --- وظائف المساعدة ---
async def check_subscribe(client, message):
    try:
        await client.get_chat_member(CHANNEL_USER, message.from_user.id)
    except UserNotParticipant:
        await message.reply_text(
            f"⚠️ **عذراً عزيزي، عليك الاشتراك في القناة أولاً:**\n👉 @{CHANNEL_USER}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("اضغط هنا للاشتراك 📢", url=f"https://t.me/{CHANNEL_USER}")]])
        )
        return False
    except: return True
    return True

# --- أوامر المطور (التحكم والحظر) ---
@app.on_message(filters.regex("^التحكم$") & filters.user(OWNER_ID))
async def admin_panel(client, message):
    u_count, g_count, b_count = len(stats["users"]), len(stats["groups"]), len(banned_users)
    await message.reply_text(
        f"📊 **لوحة تحكم المطور Cristal**\n\n"
        f"👥 **المستخدمين:** `{u_count}`\n"
        f"🏘 **المجموعات:** `{g_count}`\n"
        f"🚫 **المحظورين:** `{b_count}`\n\n"
        "**الأوامر:**\n"
        "• `حظر + الايدي`\n"
        "• `الغاء حظر + الايدي`\n"
        "• `اذاعة` (بالرد على رسالة)",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 تحديث", callback_data="refresh_stats")]])
    )

@app.on_message(filters.regex(r"^حظر (\d+)") & filters.user(OWNER_ID))
async def ban_handler(client, message):
    user_id = int(message.matches[0].group(1))
    if user_id not in banned_users:
        banned_users.append(user_id)
        save_data(BANNED_FILE, banned_users)
        await message.reply_text(f"✅ تم حظر `{user_id}`")

# --- أوامر المجموعات (الاوامر، المطور، السورس) ---
@app.on_message(filters.regex("^الاوامر$") & filters.group)
async def group_cmds(client, message):
    await message.reply_text("✨ **أوامر التشغيل:**\n• شغل + اسم الاغنية\n• ايقاف، مؤقت، استئناف، تخطي")

@app.on_message(filters.regex("^المطور$") & filters.group)
async def dev_info(client, message):
    await message.reply_text(f"👤 **المطور:** @{OWNER_USER}")

@app.on_message(filters.regex("^السورس$") & filters.group)
async def source_info(client, message):
    await message.reply_text(f"📥 **السورس:** @{CHANNEL_USER}")

# --- رسالة Start في الخاص ---
@app.on_message(filters.command("start") & filters.private)
async def start_private(client, message):
    if not await check_subscribe(client, message): return
    if str(message.from_user.id) not in stats["users"]:
        stats["users"].append(str(message.from_user.id))
        save_data(STATS_FILE, stats)
    
    await message.reply_photo(
        photo=START_IMG,
        caption=f"👋 **أهلاً بك {message.from_user.mention} في بوت كرستال**\n\n📌 أرسل `الاوامر` لمعرفة كيفية التشغيل.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎵 أضفني لمجموعتك", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")],
            [InlineKeyboardButton("👤 المطور", url=f"https://t.me/{OWNER_USER}"), InlineKeyboardButton("📢 القناة", url=f"https://t.me/{CHANNEL_USER}")]
        ])
    )

# --- نظام التشغيل (مع الطابور والاستقرار) ---
queue = {}

@app.on_message(filters.text & filters.regex(r"^(شغل|تشغيل)\s+(.*)"))
async def play_handler(client, message):
    if message.from_user.id in banned_users: return await message.reply("🚫 أنت محظور.")
    if not await check_subscribe(client, message): return
    
    # تسجيل المجموعة
    if str(message.chat.id) not in stats["groups"]:
        stats["groups"].append(str(message.chat.id))
        save_data(STATS_FILE, stats)

    query = message.matches[0].group(2)
    chat_id = message.chat.id
    m = await message.reply_text("🔎 **جاري البحث...**")

    try:
        search = VideosSearch(query, limit=1).result()['result'][0]
        title, url, thumb = search['title'], search['link'], search['thumbnails'][0]['url']
        
        with yt_dlp.YoutubeDL({"format": "bestaudio[ext=m4a]", "quiet": True}) as ydl:
            audio_url = ydl.extract_info(url, download=False)['url']

        if chat_id in queue and len(queue[chat_id]) > 0:
            queue[chat_id].append({"title": title, "url": audio_url})
            return await m.edit(f"📝 **تمت الإضافة:** {title}")

        await call_py.join_group_call(chat_id, MediaStream(audio_url))
        queue[chat_id] = [{"title": title, "url": audio_url}]
        await m.delete()
        await message.reply_photo(photo=thumb, caption=f"✅ **بدأ التشغيل:**\n`{title}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏹ إيقاف", callback_data="stop")]]))
    except Exception as e: await m.edit(f"❌ خطأ: {e}")

# --- التشغيل الرئيسي ---
async def main():
    await app.start()
    await call_py.start()
    print("💎 Cristal Music Online!")
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
