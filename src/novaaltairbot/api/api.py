import aiohttp
from typing import Optional, Any
from novaaltairbot.api.schemas import *

class NeoForestlyApi():
    def __init__(self, api_path: str, bot_api_key: str):
        self.headers = {"X-API-Key": bot_api_key}
        self.base_url = api_path
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=10.0)
        self.session = aiohttp.ClientSession(
            base_url=self.base_url,
            headers=self.headers,
            timeout=timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    
    async def new_user(self, new_user: UserIn) -> UserOut:
        async with self.session.post(
            "/user/new",
            json=new_user.model_dump(),
        ) as response:
            data = await response.json()
            return UserOut(**data)
    
    