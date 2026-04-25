import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL = "deepseek-chat"

    BOT_NAME = os.getenv("BOT_NAME", "绫地宁宁")
    BOT_PORT = int(os.getenv("BOT_PORT", 8080))

    NAPCAT_URL = os.getenv("NAPCAT_URL", "http://localhost:3000")

    MAX_HISTORY = 20
    TEMPERATURE = 0.9
    MAX_TOKENS = 3200 

    MIN_REPLY_DELAY = 0.5
    MAX_REPLY_DELAY = 2.0

    # 邮件配置
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
    SMTP_USER = os.getenv("SMTP_USER") 
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") 
    RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL") 

config = Config()
