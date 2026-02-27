import asyncio
import yt_dlp
import json
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from youtubesearchpython import VideosSearch
from config import API_ID, API_HASH, BOT_TOKEN

# --- الإعدادات ---
OWNER_ID = 8074717568  # الأيدي الخاص بك
app = Client("CristalMusic", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# --- نظام الملفات (إحصائيات وحظر) ---
STATS_FILE = "stats.json"
BANNED_FILE = "banned.json"

def load_data(file, default):
    if not os.path.exists(file): return default
    with open(file, "r") as f:
        try: return json.load(f)
        except: return default

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f)

# تحضير البيانات
stats = load_data(STATS_FILE, {"users": [], "groups": [], "channels": []})
banned_users = load_data(BANNED_FILE, [])

# --- فحص الحظر ---
async def is_banned(_, __, message):
    return message.from_user.id in banned_users

banned_filter = filters.create(is_banned)

# --- لوحة التحكم ---
@app.on_message(filters.regex("^التحكم$") & filters.user(OWNER_ID))
async def admin_panel(client, message):
    u_count = len(stats["users"])
    g_count = len(stats["groups"])
    b_count = len(banned_users)
    
    await message.reply_text(
        f"**📊 لوحة تحكم المطور Cristal**\n\n"
        f"**👥 المستخدمين:** `{u_count}`\n"
        f"**🏘 المجموعات:** `{g_count}`\n"
        f"**🚫 المحظورين:** `{b_count}`\n\n"
        "**الأوامر المتاحة:**\n"
        "• `حظر + الايدي` : لحظر عضو\n"
        "• `الغاء حظر + الايدي` : لفك حظر عضو",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 تحديث الإحصائيات", callback_data="refresh_stats")],
            [InlineKeyboardButton("📜 قائمة المحظورين", callback_data="show_banned")]
        ])
    )

# --- أوامر الحظر وفك الحظر ---
@app.on_message(filters.regex(r"^حظر (\d+)") & filters.user(OWNER_ID))
async def ban_user(client, message):
    user_id = int(message.matches[0].group(1))
    if user_id not in banned_users:
        banned_users.append(user_id)
        save_data(BANNED_FILE, banned_users)
        await message.reply_text(f"✅ تم حظر المستخدم `{user_id}` بنجاح.")
    else:
        await message.reply_text("⚠️ هذا المستخدم محظور بالفعل.")

@app.on_message(filters.regex(r"^الغاء حظر (\d+)") & filters.user(OWNER_ID))
async def unban_user(client, message):
    user_id = int(message.matches[0].group(1))
    if user_id in banned_users:
        banned_users.remove(user_id)
        save_data(BANNED_FILE, banned_users)
        await message.reply_text(f"✅ تم فك حظر المستخدم `{user_id}`.")
    else:
        await message.reply_text("⚠️ هذا المستخدم ليس في قائمة الحظر.")

# --- نظام التشغيل (يمنع المحظورين) ---
@app.on_message(filters.text & filters.regex(r"^(شغل|تشغيل)\s+(.*)") & ~banned_filter)
async def play_handler(client, message):
    # تحديث الإحصائيات
    cid = str(message.chat.id)
    if message.chat.type == "private" and cid not in stats["users"]:
        stats["users"].append(cid)
    elif message.chat.type in ["group", "supergroup"] and cid not in stats["groups"]:
        stats["groups"].append(cid)
    save_data(STATS_FILE, stats)

    query = message.matches[0].group(2)
    m = await message.reply_text("🔎 **جاري البحث...**")
    
    try:
        search = VideosSearch(query, limit=1)
        res = search.result()['result'][0]
        video_url = res['link']
        
        with yt_dlp.YoutubeDL({"format": "bestaudio[ext=m4a]", "quiet": True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            audio_url = info['url']

        await call_py.join_group_call(message.chat.id, MediaStream(audio_url))
        await m.edit(f"✅ **بدأ التشغيل:**\n`{res['title']}`")
    except Exception as e:
        await m.edit(f"❌ خطأ: `{e}`")

# رسالة للمحظورين
@app.on_message(filters.text & filters.regex(r"^(شغل|تشغيل)") & banned_filter)
async def banned_msg(client, message):
    await message.reply_text("🚫 **عذراً، لقد تم حظرك من استخدام البوت من قبل المطور.**")

@app.on_callback_query()
async def cb_handler(client, query):
    if query.data == "refresh_stats":
        await query.answer("تم التحديث ✅")
    elif query.data == "show_banned":
        await query.answer(f"عدد المحظورين: {len(banned_users)}", show_alert=True)

async def main():
    await app.start()
    await call_py.start()
    print("🚀 Cristal Music with Ban System Online!")
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
