import redis.asyncio as asyncredis

from src.config import Config
from src.auth.utils import ACCESS_TOKEN_EXPIRY


JTI_EXPIRY = ACCESS_TOKEN_EXPIRY


token_blocklist = asyncredis.Redis(
    host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0, decode_responses=True
)


async def add_jti_to_blocklist(jti: str):
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)


async def check_token_in_block_list(jti: str) -> bool:
    jti = await token_blocklist.get(jti)
    return jti is not None
