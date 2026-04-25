import os
import re
import httpx
import asyncio
from fastapi import APIRouter, Request
from loguru import logger
from config import config
from engine.aiEngine.aiEngine import ai
from engine.messageUtils.messageUtils import typing_delay
from engine.memoryManager.memoryManager import MemoryManager
from engine.cfEngine.cfEngine import get_cf_info
from engine.searchEngine.searchEngine import search_image_url
from engine.imageUtils.imageUtils import download_image, find_local_image

router = APIRouter(prefix="/qq")
memory = MemoryManager()

async def send_msg(user_id, message):
    img_dir = os.path.abspath("assets/images")
    tags = re.findall(r"\[表情:\s*(.*?)\]", message)
    processed = message
    
    for tag in tags:
        local_path = find_local_image(tag)
        if not local_path:
            url = search_image_url(tag)
            if url: local_path = await download_image(url, tag)
        if local_path:
            cq = f"[CQ:image,file=file:///{local_path.replace('\\', '/')}]"
            processed = processed.replace(f"[表情: {tag}]", cq).replace(f"[表情:{tag}]", cq)
        else:
            processed = processed.replace(f"[表情: {tag}]", f"[{tag}]").replace(f"[表情:{tag}]", f"[{tag}]")

    async with httpx.AsyncClient() as client:
        await client.post(f"{config.NAPCAT_URL}/send_private_msg", json={"user_id": user_id, "message": processed}, timeout=10)

HELP_TEXT = """🌸 宁宁的使用手册 (Skill List) 🌸

(隔着屏幕叹气) 哈啊……连这种事都要问我吗？你是笨蛋吗？

【常用指令】
· /help 或 /h : 展示这个说明
· /cf [ID] : 查 Codeforces 战力
· /学这个 [名] : 教我记住当前的表情包
· /清除记忆 : 让我暂时忘记刚才的胡言乱语

【隐藏技能】
· 识图：直接发图，我会用魔女之眼点评
· 搜索：问我实时新闻或天气，我会去联网
· 文档：问我 assets/docs 里的知识点，我会查阅
· 邮件：明确要求发邮件，我会投递到你的邮箱
· B站：问我热门视频，我会列出真实数据和封面

(盯——) 别光顾着看说明，快去写代码啦！"""

@router.post("/webhook")
async def webhook(request: Request):
    try: data = await request.json()
    except: return {"status": "error"}

    if data.get("post_type") != "message" or data.get("message_type") != "private":
        return {"status": "ignored"}

    user_id, raw_message = str(data.get("user_id", "")), data.get("raw_message", "").strip()
    user_name = data.get("sender", {}).get("nickname", "宝贝")
    
    if not raw_message and not user_id: return {"status": "ignored"}
    logger.info(f"[QQ] {user_name}({user_id}): {raw_message}")

    # --- 1. 帮助指令拦截 ---
    if raw_message.lower() in ["/help", "/h", "帮助", "帮助菜单"]:
        asyncio.create_task(send_msg(int(user_id), HELP_TEXT))
        return {"status": "ok"}

    # 图片提取
    image_url = None
    img_match = re.search(r"\[CQ:image,.*?url=(.*?)\]", raw_message)
    if img_match:
        image_url = img_match.group(1).replace("&amp;", "&")
        clean_message = re.sub(r"\[CQ:image,.*?\]", "", raw_message).strip()
    else:
        clean_message = raw_message

    # 指令处理
    if "/学这个" in raw_message and image_url:
        name_match = re.search(r"/学这个\s*(.*)", clean_message)
        name = name_match.group(1).strip() if name_match else "未命名"
        await download_image(image_url, name)
        asyncio.create_task(send_msg(int(user_id), f"(拨弄发尾) 哼，这种表情我记住了。"))
        return {"status": "ok"}

    if clean_message == "/清除记忆":
        memory.clear(user_id)
        asyncio.create_task(send_msg(int(user_id), "记忆清空了哦。"))
    elif clean_message.startswith("/cf "):
        asyncio.create_task(send_msg(int(user_id), await get_cf_info(clean_message[4:].strip())))
    else:
        asyncio.create_task(_reply(user_id, user_name, clean_message, int(user_id), image_url))
    return {"status": "ok"}

async def _reply(u_id, u_name, msg, qq_id, image_url=None):
    reply = await ai.chat(u_id, u_name, msg, image_url)
    await typing_delay(reply)
    await send_msg(qq_id, reply)
