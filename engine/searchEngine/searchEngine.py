from duckduckgo_search import DDGS
from loguru import logger

def search_web(query, max_results=5):
    try:
        logger.info(f"Searching: {query}")
        with DDGS() as ddgs:
            results = [f"Title: {r['title']}\nSnippet: {r['body']}" for r in ddgs.text(query, region='wt-wt', timelimit='y')]
            return "\n\n".join(results[:max_results]) if results else "No results found."
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Search error: {e}"

def search_image_url(query):
    """搜索一张图片的 URL"""
    try:
        logger.info(f"Searching Image: {query}")
        with DDGS() as ddgs:
            results = list(ddgs.images(f"{query} 表情包", region='wt-wt', safesearch='off'))
            return results[0]['image'] if results else None
    except Exception as e:
        logger.error(f"Image search failed: {e}")
        return None
