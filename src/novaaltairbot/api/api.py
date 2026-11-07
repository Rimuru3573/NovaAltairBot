import aiohttp
from typing import Optional
from novaaltairbot.api.schemas import (
    UserIn, UserInUsername, UserOut, Key, NewKeyIn
)
from novaaltairbot.errors import (
    XuiNameException, XuiException, KeyNotFound, TelegramIdAlreadyExists, DbAddException, UserNotFound, CustomException
)

class NovaAltairApi():
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
        async with self.session.post("/user/new", json=new_user.model_dump()) as response:
            if response.status == 201:
                data = await response.json()
                return UserOut(**data)
            elif response.status == 409:
                raise TelegramIdAlreadyExists()
            else: raise CustomException()

    async def new_key(self, new_key: NewKeyIn) -> Key:
        async with self.session.post("/user/key/add", json=new_key.model_dump()) as response:
            if response.status == 201:
                data = await response.json()
                return Key(**data)
            elif response.status == 409:
                raise XuiNameException()
            elif response.status == 500:
                raise XuiException()
            elif response.status == 400:
                raise DbAddException()
            else: raise CustomException()

    async def set_not_new(self, user: UserInUsername) -> UserOut:
        async with self.session.post("/user/set/not_new", json=user.model_dump()) as response:
            if response.status == 201:
                data = await response.json()
                return UserOut(**data)
            elif response.status == 404:
                raise UserNotFound()
            else: raise CustomException()


    async def get_key(self, email: str) -> Key:
        async with self.session.get(f"/user/key/get/{email}") as response:
            if response.status == 200:
                data =await response.json()
                return Key(**data)
            elif response.status == 404:
                raise KeyNotFound()
            else: raise CustomException()

    async def get_user(self, username: str) -> UserOut:
        async with self.session.get(f"/get/username/{username}") as response:
            if response.status == 200:
                data = await response.json()
                return UserOut(**data)
            elif response.status == 404:
                raise UserNotFound()
            else: raise CustomException()
    