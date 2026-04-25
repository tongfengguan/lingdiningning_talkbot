import os
import random
import uvicorn
import asyncio
from fastapi import FastAPI
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from engine.qqAdapter.qqAdapter import router as qq_router, send_msg
from engine.aiEngine.aiEngine import ai

# --- 屏蔽 Windows asyncio 的 10054 报错噪音 ---
import sys
if sys.platform == 'win32':
    from asyncio import proactor_events
    def _call_connection_lost_patch(self, exc=None):
        try:
            self._sock.shutdown(1) # SHUT_WR
            self._sock.close()
        except:
            pass
    proactor_events._ProactorBasePipeTransport._call_connection_lost = _call_connection_lost_patch
# -------------------------------------------

os.makedirs("logs", exist_ok=True)
logger.add("logs/bot_{time:YYYY-MM-DD}.log", rotation="1 day", retention="7 days")

app = FastAPI()
app.include_router(qq_router)

ADMIN_QQ = int(os.getenv("ADMIN_QQ", 0))

async def proactive_message():
    if not ADMIN_QQ: return
    greetings = [
        "(哈啊……) 喂，看看，你在干嘛呢？",
        "还在忙吗？笨蛋，记得休息一下！",
        "刚才看到个有趣的东西，回我一下嘛。",
        "你是失踪了吗？还是把我忘了？"
    ]
    msg = random.choice(greetings)
    await send_msg(ADMIN_QQ, msg)
    logger.info(f"Proactive push to {ADMIN_QQ}")

@app.on_event("startup")
async def startup():
    logger.info(f"🌸 {config.BOT_NAME} Started on {config.BOT_PORT}")
    # 同步 RAG 知识库
    asyncio.create_task(ai.sync_all())
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(proactive_message, 'cron', hour='10,14,18,22', minute='30')
    scheduler.start()

if __name__ == "__main__":
    # 使用较轻量级的配置运行
    uvicorn.run("main:app", host="0.0.0.0", port=config.BOT_PORT, reload=False, loop="asyncio")
