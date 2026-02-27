import sys
import pyrogram.errors

# إضافة الخطأ الناقص يدوياً إلى مكتبة بايروجرام قبل تحميل أي شيء آخر
if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    setattr(pyrogram.errors, "GroupcallForbidden", type("GroupcallForbidden", (Exception,), {}))

from CristalMusic.bot import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
