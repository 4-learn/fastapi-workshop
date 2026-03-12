from fastapi import FastAPI

app = FastAPI(title="Workshop 解答：Part 1 Path")

# 學生餐廳菜單
MENU = {
    "fried-rice": {"name": "炒飯", "price": 80},
    "noodle-soup": {"name": "湯麵", "price": 70},
    "chicken-cutlet": {"name": "雞排", "price": 60},
}


@app.get("/menu")
def list_menu():
    """列出所有餐點"""
    return MENU


@app.get("/menu/{item_id}")
def get_menu_item(item_id: str):
    """用 Path 取得指定餐點"""
    if item_id not in MENU:
        return {"error": f"找不到餐點：{item_id}"}
    item = MENU[item_id]
    return {"item_id": item_id, "name": item["name"], "price": item["price"]}


@app.get("/menu/{item_id}/reviews/{review_id}")
def get_review(item_id: str, review_id: int):
    """多層 Path：取得某餐點的某則評價"""
    return {
        "item_id": item_id,
        "review_id": review_id,
        "comment": "好好吃！",
        "rating": 5,
    }
