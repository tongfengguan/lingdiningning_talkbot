import httpx
import os
from loguru import logger

async def download_image(url, name):
    """下载图片到 assets/images"""
    path = os.path.abspath(f"assets/images/{name}.jpg")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                with open(path, "wb") as f:
                    f.write(resp.content)
                logger.info(f"Image saved: {path}")
                return path
    except Exception as e:
        logger.error(f"Download failed: {e}")
    return None

def find_local_image(name):
    """查找本地图片"""
    img_dir = os.path.abspath("assets/images")
    for ext in ['.jpg', '.png', '.gif', '.jpeg']:
        path = os.path.join(img_dir, f"{name}{ext}")
        if os.path.exists(path):
            return path
    return None
