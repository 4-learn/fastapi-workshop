from fastapi import FastAPI
import time
import asyncio

app = FastAPI()


# ── 基本 ping，用來測試 API 是否被卡住 ──────────────────────────────────────
@app.get("/ping")
async def ping():
    return {"status": "pong"}


# ── 題目 3 修改前：阻塞版本（time.sleep 堵住 event loop）──────────────────
@app.get("/sync")
async def sync_api():
    # ❌ time.sleep 是同步操作，會把整條 thread（含 event loop）凍結 5 秒
    # 這段時間任何其他 request（包含 /ping）全部卡住，等它結束才能繼續
    time.sleep(5)
    return {"status": "done"}


# ── 題目 3 修改後：非阻塞版本（await asyncio.sleep 讓出 event loop）────────
@app.get("/async")
async def async_api():
    # ✅ await 會把控制權交還給 event loop
    # event loop 趁這 5 秒去處理其他 request（例如 /ping 可以馬上回應）
    # 5 秒到了再回來繼續執行這個 coroutine
    await asyncio.sleep(5)
    return {"status": "done"}
