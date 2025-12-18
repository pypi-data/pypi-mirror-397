import os
from supabase import create_async_client
import logging

logger = logging.getLogger(__name__)


async def get_supabase_async():
    """
    获取异步 Supabase 客户端 (Service Role 权限)
    """
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise ValueError(
            "Missing NEXT_PUBLIC_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables"
        )

    logger.info(f"Connecting to Supabase: {url}")
    return await create_async_client(url, key)
