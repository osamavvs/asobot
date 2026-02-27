from pyrogram import Client
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
        print("✅ البوت اشتغل بنجاح!")

    async def stop(self, *args):
        await super().stop()
        print("❌ تم إيقاف البوت.")

app = Bot()

async def main():
    await app.start()
    # هنا يتم إضافة سطور إضافية لتشغيل الـ plugins
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
