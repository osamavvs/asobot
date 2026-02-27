import os
from dotenv import load_dotenv

load_dotenv()

# --- حقوق سورس كرستال ---
MUSIC_BOT_NAME = "بوت كرستال للموسيقى" 
OWNER_ID = 12345678 # ضع الأيدي الخاص بك هنا
SUPPORT_CHANNEL = "https://t.me/YourChannel" # قناتك
SUPPORT_GROUP = "https://t.me/YourGroup" # جروبك

# --- إعدادات التشغيل ---
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_DB_URI = os.getenv("MONGO_DB_URI")
STRING_SESSION = os.getenv("STRING_SESSION")
