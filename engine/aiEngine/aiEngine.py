import httpx
import random
import re
import asyncio
from loguru import logger
from config import config
from engine.memoryManager.memoryManager import MemoryManager
from engine.persona.persona import build_prompt
from engine.searchEngine.searchEngine import search_web
from engine.emailEngine.emailEngine import send_email_to_user
from engine.pdfEngine.pdfEngine import pdf_engine
from engine.imageUtils.visionEngine import analyze_image
from engine.biliEngine.biliEngine import get_bili_popular

class AIGirlfriend:
    def __init__(self):
        self.memory = MemoryManager()
        self.headers = {"Authorization": f"Bearer {config.DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        logger.info(f"[{config.BOT_NAME}] Natural Chat Mode Loaded")

    async def _ai_call(self, messages, temp=None, tokens=None):
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(f"{config.DEEPSEEK_BASE_URL}/chat/completions", headers=self.headers, json={
                "model": config.DEEPSEEK_MODEL, "messages": messages, "temperature": temp or config.TEMPERATURE, "max_tokens": tokens or config.MAX_TOKENS
            })
            return resp.json()["choices"][0]["message"]["content"].strip()

    async def chat(self, user_id, user_name, message, image_url=None):
        try:
            self.memory.upsert_user(user_id, user_name)
            
            # 1. 意图并行分析
            tasks = [
                self._ai_call([
                    {"role": "system", "content": "指令器：联网搜'WEB:关键词'，查文档'DOC:关键词'，看B站'BILI'，否则'NO'。"},
                    {"role": "user", "content": message}
                ], temp=0.1, tokens=50)
            ]
            if image_url: tasks.append(analyze_image(image_url))
            else: tasks.append(asyncio.sleep(0, ""))
            
            decision, vision_desc = await asyncio.gather(*tasks)

            # 2. 资料抓取
            context_text = ""
            is_bili = "BILI" in decision.upper()
            bili_append_data = ""

            if is_bili:
                videos = await get_bili_popular(limit=10)
                if videos:
                    v = random.choice(videos)
                    def fmt(n): return f"{n/1000:.1f}k" if n >= 1000 else str(n)
                    bili_append_data = (
                        f"📺 【B站热门精选】\n"
                        f"[CQ:image,file={v['cover']}]\n"
                        f"标题：{v['title']}\n"
                        f"UP主：{v['author']}\n"
                        f"点赞：{fmt(v['like'])} 投币：{fmt(v['coin'])}\n"
                        f"收藏：{fmt(v['favorite'])} 观看：{fmt(v['view'])}\n"
                        f"链接：{v['url']}"
                    )
                    context_text = f"\n[B站数据]: {v['title']}，观看{fmt(v['view'])}。"

            elif decision.startswith("WEB:"):
                context_text = f"\n[联网结果]:\n{search_web(decision[4:])}"
            elif decision.startswith("DOC:"):
                context_text = f"\n[文档参考]:\n{await pdf_engine.search_docs(decision[4:])}"

            # 3. 构造回复 - 彻底去除强制吐槽指令
            prompt = build_prompt(config.BOT_NAME, user_name)
            if vision_desc: prompt += f"\n【看到图片】: {vision_desc}"
            
            if is_bili:
                prompt += f"\n{context_text}\n【指令】请对上面的B站热门视频发表你的看法。你可以根据视频内容决定是吐槽、赞赏还是单纯觉得无聊。"
            elif context_text:
                prompt += f"\n{context_text}\n请结合资料，以你的人设进行自然回复。"
            
            prompt += f"\n【提醒】邮箱 {config.RECEIVER_EMAIL} 可用。代码回复不受限。"

            messages = [{"role": "system", "content": prompt}]
            messages.extend(self.memory.get_history(user_id, config.MAX_HISTORY))
            messages.append({"role": "user", "content": message if message else "你看这张图？"})

            reply = await self._ai_call(messages)

            # 4. 组装
            final_reply = (bili_append_data + "\n\n" + reply) if (is_bili and bili_append_data) else reply

            # 邮件拦截
            if "[ACTION: SEND_EMAIL" in final_reply:
                match = re.search(r"\[ACTION: SEND_EMAIL\|(.*?)\|(.*?)\]", final_reply, re.S)
                if match:
                    send_email_to_user(match.group(1), match.group(2), config.RECEIVER_EMAIL)
                    final_reply = re.sub(r"\[ACTION: SEND_EMAIL\|.*?\]", "", final_reply, flags=re.S).strip()

            # 异步保存
            self.memory.save(user_id, "user", message or "[图片]")
            self.memory.save(user_id, "assistant", final_reply)
            asyncio.create_task(self.memory.index_chat(user_id, "user", message))
            asyncio.create_task(self.memory.index_chat(user_id, "assistant", final_reply))
            
            return final_reply
        except Exception as e:
            logger.error(f"Chat Error: {e}")
            return "刚才走神了……"

    async def sync_all(self):
        await pdf_engine.sync_docs()

ai = AIGirlfriend()
