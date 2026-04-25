import httpx
import os
from loguru import logger

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

async def analyze_image(image_url):
    """调用阿里 Qwen-VL 模型分析图片"""
    if not DASHSCOPE_API_KEY:
        logger.warning("未配置 DASHSCOPE_API_KEY，视觉分析跳过。")
        return "（宁宁没带眼镜，看不清图里的细节，只能猜个大概）"

    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen-vl-plus",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"image": image_url},
                        {"text": "请简要描述这张图片的内容，如果是代码请提取关键信息，如果是人物请描述神态。"}
                    ]
                }
            ]
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, json=payload)
            result = resp.json()
            description = result['output']['choices'][0]['message']['content'][0]['text']
            logger.info(f"视觉分析结果: {description}")
            return description
    except Exception as e:
        logger.error(f"视觉分析出错: {e}")
        return "（图里有一层迷雾，宁宁看不清呢）"
