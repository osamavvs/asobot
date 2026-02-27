import asyncio
import pyrogram.errors

# حل مشكلة الإصدارات قبل التحميل
if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    setattr(pyrogram.errors, "GroupcallForbidden", type("GroupcallForbidden", (Exception,), {}))

from CristalMusic.bot import main

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
