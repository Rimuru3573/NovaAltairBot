import inspect

from yarl import URL

print("join abs path:", URL("http://127.0.0.1:8000").join(URL("/user/new")))
print("join with base path:", URL("http://host/api").join(URL("/user/new")))
print("join with base path+slash:", URL("http://host/api/").join(URL("user/new")))

import aiohttp

try:
    s = aiohttp.ClientSession(base_url="http://127.0.0.1:8000")
    print("session with bare base_url: OK")
except Exception as e:
    print("session error:", type(e).__name__, e)

from aiogram import Dispatcher

print("\nstart_polling signature:", inspect.signature(Dispatcher.start_polling))
src = inspect.getsource(Dispatcher.start_polling)
print("start_polling references session.close:", "session.close" in src)

import aiogram.client.session.aiohttp as a

print("\nAiohttpSession.__init__:", inspect.signature(a.AiohttpSession.__init__))

# what does dispatcher send in allowed_updates by default?
src2 = inspect.getsource(Dispatcher._polling)
print("\n_polling snippet:")
for line in src2.splitlines():
    if "allowed_updates" in line or "resolve_used" in line:
        print("   ", line.strip())
