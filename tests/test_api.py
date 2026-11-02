from novaaltairbot.api.api import NovaAltairApi
from novaaltairbot.api.schemas import *
from novaaltairbot.config import settings






async def test_new_user():
    async with NovaAltairApi(settings.api_path, settings.bot_api_key) as api:
        response = await api.new_user(new_user=UserIn(username="test123", password="test", telegram_id=12345678))
        assert response.username == "test123"

async def test_add_key():
    pass