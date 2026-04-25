import os
from pypdf import PdfReader
from loguru import logger
from engine.ragEngine.ragEngine import rag_engine

class PDFEngine:
    def __init__(self, docs_dir="assets/docs"):
        self.docs_dir = os.path.abspath(docs_dir)
        os.makedirs(self.docs_dir, exist_ok=True)

    def extract_text(self, filename):
        path = os.path.join(self.docs_dir, filename)
        if not os.path.exists(path): return None
        try:
            reader = PdfReader(path)
            return "\n".join([page.extract_text() for page in reader.pages])
        except Exception as e:
            logger.error(f"Failed to extract {filename}: {e}")
            return None

    async def sync_docs(self):
        """同步本地 PDF 到向量库"""
        files = [f for f in os.listdir(self.docs_dir) if f.endswith('.pdf')]
        for file in files:
            # 简单判断是否已索引过 (根据 source 字段)
            if any(d['source'] == file for d in rag_engine.data):
                continue
            
            logger.info(f"Indexing new PDF: {file}")
            text = self.extract_text(file)
            if text:
                chunks = rag_engine.add_text(text, source=file)
                await rag_engine.index_chunks(chunks, source=file)
        logger.info("PDF Sync Complete")

    async def search_docs(self, query):
        """语义检索"""
        results = await rag_engine.search(query, top_k=3)
        if not results: return ""
        
        formatted = []
        for r in results:
            formatted.append(f"--- 来自 {r['source']} ---\n{r['text']}")
        return "\n\n".join(formatted)

pdf_engine = PDFEngine()
