import asyncio
import random
from config import config

async def typing_delay(text):
    delay = random.uniform(config.MIN_REPLY_DELAY, config.MAX_REPLY_DELAY) + len(text) * 0.03
    await asyncio.sleep(min(delay, 4.0))
