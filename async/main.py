from fastapi import FastAPI
from tasks import async_infinite_loop

app = FastAPI()


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.get("/sync")
async def sync_api():
    """解答：改用 await async_infinite_loop，不阻塞 event loop"""
    await async_infinite_loop()
    return {"message": "done"}


@app.get("/async")
async def async_api():
    """使用 await asyncio.sleep，不會阻塞"""
    await async_infinite_loop()
    return {"message": "done"}
