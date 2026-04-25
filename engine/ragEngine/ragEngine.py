import os
import json
import httpx
import numpy as np
from loguru import logger
from config import config

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

async def get_embedding(text):
    """调用阿里 DashScope 文本向量接口"""
    if not DASHSCOPE_API_KEY:
        logger.warning("未配置 DASHSCOPE_API_KEY，无法使用 RAG。")
        return None

    url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "text-embedding-v2",
        "input": {"texts": [text]}
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(url, headers=headers, json=payload)
            result = resp.json()
            return result['output']['embeddings'][0]['embedding']
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return None

class RAGEngine:
    def __init__(self, storage_path="data/vector_store.json"):
        self.storage_path = storage_path
        self.data = [] # 格式: [{"text": str, "vec": list, "source": str}]
        self.load()

    def add_text(self, text, source="unknown", chunk_size=400, overlap=50):
        """对文本进行切块并准备入库"""
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i : i + chunk_size]
            if len(chunk) > 10: # 过滤太短的垃圾块
                chunks.append(chunk)
        return chunks

    async def index_chunks(self, chunks, source):
        """异步向量化并存入内存"""
        for chunk in chunks:
            # 简单去重
            if any(d['text'] == chunk for d in self.data):
                continue
            vec = await get_embedding(chunk)
            if vec:
                self.data.append({"text": chunk, "vec": vec, "source": source})
        self.save()

    async def search(self, query, top_k=3):
        """向量相似度检索"""
        query_vec = await get_embedding(query)
        if not query_vec or not self.data:
            return []

        q_v = np.array(query_vec)
        results = []
        for item in self.data:
            i_v = np.array(item['vec'])
            # 余弦相似度
            score = np.dot(q_v, i_v) / (np.linalg.norm(q_v) * np.linalg.norm(i_v))
            results.append((score, item))
        
        # 按分数排序并取 Top K
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:top_k] if r[0] > 0.6] # 阈值 0.6

    def save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False)

    def load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except:
                self.data = []

rag_engine = RAGEngine()
