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

class AIGirlfriend:
    def __init__(self):
        self.memory = MemoryManager()
        self.headers = {"Authorization": f"Bearer {config.DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        logger.info(f"[{config.BOT_NAME}] RAG-Enabled Engine Initialized")

    async def sync_all(self):
        """同步所有本地知识库"""
        await pdf_engine.sync_docs()

    async def chat(self, user_id, user_name, message, image_url=None):
        try:
            self.memory.upsert_user(user_id, user_name)
            
            # 1. 异步并行获取视觉信息、RAG信息和联网信息 (如果需要)
            # 为了极致性能，我们先获取本地 RAG 和视觉
            tasks = []
            if image_url: tasks.append(analyze_image(image_url))
            else: tasks.append(asyncio.sleep(0, "")) # 占位
            
            # 语义检索：同时查 PDF 和 长期记忆
            tasks.append(pdf_engine.search_docs(message))
            tasks.append(self.memory.get_long_term_memory(message))
            
            vision_desc, doc_context, long_term_mem = await asyncio.gather(*tasks)

            # 2. 构造上下文
            context = ""
            if doc_context: context += f"\n[参考本地文档]:\n{doc_context}"
            if long_term_mem: context += f"\n[回忆起的相关往事]:\n{long_term_mem}"
            
            # 3. 构造回复逻辑
            prompt = build_prompt(config.BOT_NAME, user_name)
            if vision_desc:
                prompt += f"\n【魔女之眼观测到的图片】: {vision_desc}"
            if context:
                prompt += f"\n{context}\n(请结合以上参考资料，用你那高冷吐槽的风格进行回复)"
            
            prompt += f"""
【权限与指令】：
- 邮箱: {config.RECEIVER_EMAIL} (已知，无需询问)。
- 仅当明确需要时发邮件: [ACTION: SEND_EMAIL|主题|内容]。
- 默认回复 3 句内；代码/邮件不受限。
"""
            
            messages = [{"role": "system", "content": prompt}]
            messages.extend(self.memory.get_history(user_id, config.MAX_HISTORY))
            messages.append({"role": "user", "content": message if message else "你看图？"})

            # 4. 调用 AI
            async with httpx.AsyncClient(timeout=45) as client:
                resp = await client.post(f"{config.DEEPSEEK_BASE_URL}/chat/completions", headers=self.headers, json={
                    "model": config.DEEPSEEK_MODEL, "messages": messages, "temperature": config.TEMPERATURE, "max_tokens": config.MAX_TOKENS
                })
                reply = resp.json()["choices"][0]["message"]["content"].strip()

            # 5. 动作拦截与保存
            final_reply = reply
            if "[ACTION: SEND_EMAIL" in final_reply:
                match = re.search(r"\[ACTION: SEND_EMAIL\|(.*?)\|(.*?)\]", final_reply, re.S)
                if match:
                    send_email_to_user(match.group(1), match.group(2), config.RECEIVER_EMAIL)
                    final_reply = re.sub(r"\[ACTION: SEND_EMAIL\|.*?\]", "", final_reply, flags=re.S).strip()
            
            if not final_reply:
                final_reply = "(哈啊……) 已经发到你那个邮箱了，自己去翻。"

            # 异步保存到短效历史和长效向量记忆
            self.memory.save(user_id, "user", message or "[图片]")
            self.memory.save(user_id, "assistant", final_reply)
            asyncio.create_task(self.memory.index_chat(user_id, "user", message))
            asyncio.create_task(self.memory.index_chat(user_id, "assistant", final_reply))
            
            return final_reply

        except Exception as e:
            logger.error(f"Chat Error: {e}")
            return "刚才走神了，没听清你在说什么呢……"

ai = AIGirlfriend()
