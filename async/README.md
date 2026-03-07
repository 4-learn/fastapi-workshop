# Workshop 解答 – 非同步、背景任務與「不要卡 API」

## 情境

你接手一個 FastAPI 專案，發現有兩個 endpoint：`/sync` 和 `/async`。

使用者抱怨：

> 「有時候整個 API 都沒反應」

---

## 任務 1：觀察行為（不用改 code）

### 問題

1. 哪一個 endpoint 會讓 `/ping` 失效？
2. 為什麼？

### 解答

| 操作                           | `/ping` 是否正常回應 |
| ------------------------------ | -------------------- |
| 先呼叫 `/sync`，再呼叫 `/ping`  | ❌ 無回應（被阻塞）  |
| 先呼叫 `/async`，再呼叫 `/ping` | ✅ 正常回應 pong     |

**回答：**

1. `/sync` 會讓 `/ping` 失效
2. 因為 `sync_infinite_loop()` 內部使用 `time.sleep(1)`，這是同步阻塞操作，會佔住整個 event loop，導致所有其他 request（包括 `/ping`）都無法被處理

> **金句：一個 `time.sleep` 就能癱瘓整個 API。**

---

## 任務 2：概念判斷

### 問題

> 為什麼 `sync_api` 明明是 `async def`，卻仍然會卡住整個系統？

### 解答

`async def` 只是告訴 Python：「這個函式可以使用 `await`」。但**它不會自動讓裡面的程式碼變成非阻塞**。

關鍵在於函式內部做了什麼：

```python
@app.get("/sync")
async def sync_api():
    sync_infinite_loop()  # 裡面是 time.sleep → 同步阻塞
    return {"message": "done"}
```

- `time.sleep(1)` 是 **同步操作**，它會直接凍結當前執行緒
- FastAPI 的 event loop 跑在**單一執行緒**上
- 當 `time.sleep` 執行時，event loop 被凍結，無法切換去處理其他 request

對比：

```python
@app.get("/async")
async def async_api():
    await async_infinite_loop()  # 裡面是 await asyncio.sleep → 非阻塞
    return {"message": "done"}
```

- `await asyncio.sleep(1)` 會**交出控制權**給 event loop
- event loop 在等待期間可以去處理 `/ping` 等其他 request

### 一句話總結

> **`async def` 是入場券，`await` 才是讓座的動作。沒有 `await`，你就是霸佔整個座位的人。**

---

## 任務 3：改寫

### 問題

把 `sync_api` 改成「不阻塞 event loop」的版本。

### 解答

最直接的改法——改用 `async_infinite_loop`：

```python
@app.get("/sync")
async def sync_api():
    await async_infinite_loop()
    return {"message": "done"}
```

### 為什麼這樣改就好了？

| 改動前                    | 改動後                          |
| ------------------------- | ------------------------------- |
| `sync_infinite_loop()`    | `await async_infinite_loop()`   |
| 內部用 `time.sleep`       | 內部用 `await asyncio.sleep`    |
| 阻塞 event loop           | 交回控制權給 event loop         |
| `/ping` 無回應             | `/ping` 正常回應                |

### 延伸：如果一定要用同步函式呢？

如果你無法修改 `sync_infinite_loop`（例如它是第三方套件），可以用 `asyncio.to_thread` 把它丟到另一個執行緒：

```python
import asyncio

@app.get("/sync")
async def sync_api():
    await asyncio.to_thread(sync_infinite_loop)
    return {"message": "done"}
```

這樣同步阻塞會發生在**另一個執行緒**，不會卡住 event loop。

> **金句：改不了別人的 code，就把它丟到別的執行緒去。**

---

## 總結

| 觀念                        | 說明                                          |
| --------------------------- | --------------------------------------------- |
| `async def` ≠ 非阻塞        | 阻不阻塞取決於內部實作                        |
| `time.sleep` 會卡死 event loop | 同步等待，整個系統暫停                      |
| `await asyncio.sleep` 不會卡  | 非同步等待，控制權交回 event loop             |
| `asyncio.to_thread`          | 把無法修改的同步 code 丟到執行緒，避免阻塞    |

> **終極金句：`async def` 不保證你是好鄰居，`await` 才是。**
