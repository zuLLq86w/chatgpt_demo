import asyncio

from openai import OpenAI
from httpx import HTTPError, TimeoutException
from loguru import logger
from app.core.config import settings


async def create_completions_with_retry(messages, max_retry=2, delay=1, stream=True):
    client = OpenAI(
        # api_key="sk-e148ee4df9124d6390b0d05761a41921",
        api_key=settings.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com")

    for i in range(max_retry + 1):
        try:
            logger.debug(f"AI请求消息: {messages}")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=stream
            )
            return response
        except (HTTPError, TimeoutException, Exception) as e:
            if i < max_retry:
                await asyncio.sleep(delay)
                delay *= 2
                continue
            else:
                raise e

