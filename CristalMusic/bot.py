import asyncio
from pyrogram import Client, filters
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
        print("✅ البوت اشتغل بنجاح وهو الآن يستمع للأوامر!")

    async def stop(self, *args):
        await super().stop()
        print("❌ تم إيقاف البوت.")

app = Bot()

# --- قسم الأوامر ---

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        f"**أهلاً بك يا {message.from_user.mention} في بوت كرستال ميوزك!**\n\n"
        "أنا أعمل الآن بنجاح، يمكنك البدء بإرسال الأوامر."
    )

@app.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text("قائمة الأوامر حالياً:\n/start - لبدء التشغيل\n/help - للمساعدة")

# --- نهاية قسم الأوامر ---

async def main():
    await app.start()
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
