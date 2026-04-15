import json
from collections import Counter


def load_orders():
    with open("orders.json", "r", encoding="utf-8") as f:
        return json.load(f)


def extract_price(price_str):
    """从 '14.42元' 提取 14.42"""
    try:
        return float(price_str.replace("元", ""))
    except:
        return 0


def analyze_user_profile(orders):
    categories = []
    tastes = []
    shops = []
    prices = []

    for order in orders:
        # 分类
        categories.append(order.get("食物类别", "未知"))

        # 口味
        tastes.append(order.get("菜品口味", "未知"))

        # 店铺
        shops.append(order.get("店名", "未知"))

        # 价格
        prices.append(extract_price(order.get("实付款", "0元")))

    # ===== 统计 =====
    category_counter = Counter(categories)
    taste_counter = Counter(tastes)
    shop_counter = Counter(shops)

    # ===== 偏好 =====
    favorite_category = category_counter.most_common(1)[0][0]
    favorite_taste = taste_counter.most_common(1)[0][0]
    frequent_shops = [shop for shop, _ in shop_counter.most_common(3)]

    # ===== 价格分析 =====
    avg_price = sum(prices) / len(prices) if prices else 0

    if avg_price < 15:
        price_level = "偏便宜（10-15元）"
    elif avg_price < 25:
        price_level = "适中（15-25元）"
    else:
        price_level = "偏贵（25元以上）"

    # ===== 多样性分析 =====
    unique_categories = len(set(categories))

    if unique_categories <= 2:
        diversity = "饮食比较单一"
    elif unique_categories <= 4:
        diversity = "有一定多样性"
    else:
        diversity = "饮食非常多样"

    # ===== 最终画像 =====
    profile = {
        "最常吃": favorite_category,
        "口味偏好": favorite_taste,
        "常点店铺": frequent_shops,
        "平均消费": round(avg_price, 2),
        "消费水平": price_level,
        "饮食多样性": diversity
    }

    return profile


if __name__ == "__main__":
    orders = load_orders()
    profile = analyze_user_profile(orders)

    print("=== 用户画像 ===")
    for k, v in profile.items():
        print(f"{k}：{v}")