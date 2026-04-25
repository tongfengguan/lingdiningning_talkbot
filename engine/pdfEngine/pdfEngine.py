import os
import asyncio
from pypdf import PdfReader
from loguru import logger
from engine.ragEngine.ragEngine import rag_engine

class PDFEngine:
    def __init__(self, docs_dir="assets/docs"):
        self.docs_dir = os.path.abspath(docs_dir)
        os.makedirs(self.docs_dir, exist_ok=True)

    def _extract_text_sync(self, filename):
        path = os.path.join(self.docs_dir, filename)
        if not os.path.exists(path): return None
        try:
            if filename.endswith('.pdf'):
                reader = PdfReader(path)
                return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            elif filename.endswith('.txt') or filename.endswith('.md'):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Failed to extract {filename}: {e}")
            return None

    async def sync_docs(self):
        """同步本地文档 (PDF/TXT) 到向量库"""
        files = [f for f in os.listdir(self.docs_dir) if f.endswith(('.pdf', '.txt', '.md'))]
        loop = asyncio.get_event_loop()
        for file in files:
            if any(d['source'] == file for d in rag_engine.data):
                continue
            logger.info(f"正在学习新文档: {file}")
            text = await loop.run_in_executor(None, self._extract_text_sync, file)
            if text:
                chunks = rag_engine.add_text(text, source=file)
                await rag_engine.index_chunks(chunks, source=file)
        logger.info("✅ 文档学习完成，宁宁现在的记忆非常完整。")

    async def search_docs(self, query):
        if not query: return ""
        results = await rag_engine.search(query, top_k=3)
        if not results: return ""
        return "\n\n".join([f"--- 来自 {r['source']} ---\n{r['text']}" for r in results])

pdf_engine = PDFEngine()
