import sqlite3
import os
from threading import Lock
from loguru import logger
from engine.ragEngine.ragEngine import rag_engine

class MemoryManager:
    def __init__(self, db_path="data/memory.db"):
        os.makedirs("data", exist_ok=True)
        self.db_path = db_path
        self.lock = Lock()
        self._exec("""CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        self._exec("""CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY, nickname TEXT, last_active DATETIME
        )""")
        logger.info("Memory DB Initialized")

    def _exec(self, sql, params=()):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            return conn.execute(sql, params).fetchall()

    def save(self, user_id, role, content):
        self._exec("INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))

    async def index_chat(self, user_id, role, content):
        """将聊天记录存入长效向量记忆"""
        # 仅对较长的有意义内容进行向量化
        if len(content) > 10:
            chunks = [f"{role}: {content}"]
            await rag_engine.index_chunks(chunks, source=f"chat_{user_id}")

    def get_history(self, user_id, limit=20):
        rows = self._exec("SELECT role, content FROM chat_history WHERE user_id=? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
        return [{"role": r, "content": c} for r, c in reversed(rows)]

    async def get_long_term_memory(self, query, top_k=2):
        """检索长效记忆"""
        results = await rag_engine.search(query, top_k=top_k)
        # 过滤掉非聊天来源
        chat_results = [r['text'] for r in results if r['source'].startswith('chat_')]
        return "\n".join(chat_results) if chat_results else ""

    def upsert_user(self, user_id, nickname):
        self._exec("INSERT INTO users (user_id, nickname, last_active) VALUES (?, ?, datetime('now')) ON CONFLICT(user_id) DO UPDATE SET nickname=excluded.nickname, last_active=datetime('now')", (user_id, nickname))

    def clear(self, user_id):
        self._exec("DELETE FROM chat_history WHERE user_id=?", (user_id,))
        logger.info(f"Memory cleared for {user_id}")
