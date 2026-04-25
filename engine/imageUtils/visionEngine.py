import httpx
import os
from loguru import logger

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

async def analyze_image(image_url):
    """调用 Qwen-VL 分析图片，重点识别文字和情绪梗"""
    if not DASHSCOPE_API_KEY:
        return "（宁宁没带眼镜，看不清细节）"

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
                        {"text": "这是一张QQ聊天中的图片或表情包。请识别并描述图中的所有文字、主体动作及神态，并概括这张图想表达的'梗'或情绪。回复需简练。"}
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
        return "（刚才眼睛花了一下，没看清那张图的内容呢）"
