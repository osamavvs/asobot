async def main():
    await app.start()
    await call_py.start()
    print("🚀 البوت والمحرك الصوتي جاهزان!")
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
