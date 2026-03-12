from fastapi import FastAPI, Body

app = FastAPI(title="Workshop 解答：Part 3 Body")

MENU = {
    "fried-rice": {"name": "炒飯", "price": 80},
    "noodle-soup": {"name": "湯麵", "price": 70},
    "chicken-cutlet": {"name": "雞排", "price": 60},
}

orders = []


@app.post("/orders")
def create_order(order: dict = Body(...)):
    """
    送出訂單，Body 包含：
    {
        "item_id": "fried-rice",
        "quantity": 2,
        "note": "不要蔥"
    }
    """
    order_id = len(orders) + 1
    orders.append({"order_id": order_id, **order})

    item = MENU.get(order.get("item_id", ""), {})
    total = item.get("price", 0) * order.get("quantity", 1)

    return {"message": "訂餐成功", "order_id": order_id, "total": total}


@app.post("/menu/{item_id}/customize")
def customize_item(
    item_id: str,
    preview: bool = False,
    options: dict = Body(...),
):
    """
    三層一起用：
    - Path: item_id（哪個餐點）
    - Query: preview（只預覽不下單）
    - Body: options（客製化選項，如 {"extra": "加蛋", "spicy_level": 3}）
    """
    if item_id not in MENU:
        return {"error": f"找不到餐點：{item_id}"}

    result = {
        "item": MENU[item_id]["name"],
        "customization": options,
        "is_preview": preview,
    }
    if not preview:
        orders.append(result)
        result["message"] = "已下單"
    return result
