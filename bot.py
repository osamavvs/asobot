import asyncio
from pyrogram import filters, idle
from client import app, call_py # استدعاء مباشر ومضمون
from config import OWNER_ID, OWNER_USER
from pytgcalls.types import MediaStream # تأكد من أن هذا المسار يعمل في v3

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(f"💎 تم تشغيل البوت بنجاح يا بطل!")

async def main():
    await app.start()
    await call_py.start()
    print("✅ البوت يعمل الآن!")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
