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
from engine.biliEngine.biliEngine import get_bili_popular
from engine.dashboard.dashboard import router as dashboard_router

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
app.include_router(dashboard_router)

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

async def bilibili_trending_push():
    if not ADMIN_QQ: return
    logger.info("Fetching Bilibili trending videos for push...")
    videos = await get_bili_popular(limit=3)
    if not videos:
        return
    
    video_info = "\n".join([f"- {v['title']} (UP: {v['author']})\n  链接: {v['url']}" for v in videos])
    
    # 让宁宁对这些视频进行点评
    prompt = f"这是B站现在的热门视频列表：\n{video_info}\n请以你绫地宁宁的人设，挑选其中一个你觉得感兴趣（或者觉得对方会感兴趣）的视频，用你那招牌的高冷吐槽风格发给对方。记得带上视频链接。"
    
    # 使用 chat 方法，但传入特殊指令
    reply = await ai.chat(str(ADMIN_QQ), "看看", prompt)
    await send_msg(ADMIN_QQ, reply)
    logger.info(f"Bilibili trending push to {ADMIN_QQ}")

@app.on_event("startup")
async def startup():
    logger.info(f"🌸 {config.BOT_NAME} Started on {config.BOT_PORT}")
    # 同步 RAG 知识库
    asyncio.create_task(ai.sync_all())
    
    scheduler = AsyncIOScheduler()
    # 每隔 4 小时随机尝试骚扰你一下
    scheduler.add_job(proactive_message, 'cron', hour='10,14,18,22', minute='30')
    # 每天下午 6 点推送 B 站热门 (或者你可以改时间)
    scheduler.add_job(bilibili_trending_push, 'cron', hour='18', minute='00')
    scheduler.start()
    logger.info("⏰ Scheduler started with Bilibili push task")

if __name__ == "__main__":
    # 使用较轻量级的配置运行
    uvicorn.run("main:app", host="0.0.0.0", port=config.BOT_PORT, reload=False, loop="asyncio")
