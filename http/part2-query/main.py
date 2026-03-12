from fastapi import FastAPI

app = FastAPI(title="Workshop 解答：Part 2 Query")

MENU = {
    "fried-rice": {"name": "炒飯", "price": 80, "category": "飯類", "spicy": True},
    "noodle-soup": {"name": "湯麵", "price": 70, "category": "麵類", "spicy": False},
    "chicken-cutlet": {"name": "雞排", "price": 60, "category": "炸物", "spicy": True},
    "salad": {"name": "沙拉", "price": 50, "category": "輕食", "spicy": False},
}


@app.get("/menu")
def list_menu(
    category: str = None,
    max_price: int = None,
    spicy_only: bool = False,
):
    """
    用 Query 篩選餐點
    - category: 類別（飯類、麵類、炸物、輕食）
    - max_price: 價格上限
    - spicy_only: 只看辣的
    """
    results = {}
    for item_id, info in MENU.items():
        if category and info["category"] != category:
            continue
        if max_price and info["price"] > max_price:
            continue
        if spicy_only and not info["spicy"]:
            continue
        results[item_id] = info
    return results


@app.get("/menu/{item_id}")
def get_menu_item(item_id: str, lang: str = "zh"):
    """
    lang 是觀察條件：用中文或英文顯示
    不影響餐點本身 → Query
    """
    if item_id not in MENU:
        return {"error": f"找不到餐點：{item_id}"}
    name = MENU[item_id]["name"] if lang == "zh" else item_id.replace("-", " ").title()
    return {"item_id": item_id, "name": name, "price": MENU[item_id]["price"]}
