from novaaltairbot.api.api import NovaAltairApi
from novaaltairbot.api.schemas import *
from novaaltairbot.config import settings


# async def test_new_user():
#     async with NovaAltairApi(settings.api_path, settings.bot_api_key) as api:
#         response = await api.new_user(new_user=UserIn(username="test1234", password="test1", telegram_id=123456788))
#         assert response.username == "test1234"

# async def test_add_key():
#     async with NovaAltairApi(settings.api_path, settings.bot_api_key) as api:
#         response = await api.new_key(new_key=NewKeyIn(username="test1234", email="pisa_test1", day_expiry=30))
#         print(response.sub_link)
#         assert response.email == "pisa_test1"