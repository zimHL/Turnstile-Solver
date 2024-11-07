import asyncio
from async_solver import get_turnstile_token as async_get_token
from sync_solver import get_turnstile_token as sync_get_token
    
mode = input("Mode (sync/async): ").strip().lower()
url = input("URL: ").strip()
sitekey = input("Sitekey: ").strip()

async def asynchronous():
    result = await async_get_token(url=url, sitekey=sitekey)
    print("Result:", result)

def synchronous():
    result = sync_get_token(url=url, sitekey=sitekey)
    print("Result:", result)

if __name__ == "__main__":
    if mode == "async":
        asyncio.run(asynchronous())
    else:
        synchronous()
