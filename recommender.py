import json
from zhipuai import ZhipuAI
from dotenv import load_dotenv
import os

load_dotenv()
client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))

# ===== 加载数据（已加入商家池子）=====
def load_orders():
    with open("orders.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_profile():
    from user_profile import analyze_user_profile
    orders = load_orders()
    return analyze_user_profile(orders)

# ===================== 【关键】加载你的商家池子 =====================
def load_shop_pool():
    with open("nearby_shops.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ===== 推荐函数（强制从商家池推荐）=====
def recommend(user_input, profile, history_reject):
    # 加载店铺池
    shop_pool = load_shop_pool()
    shop_pool_str = json.dumps(shop_pool, ensure_ascii=False, indent=2)

    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {
                "role": "system",
                "content": f"""
你是一个外卖推荐助手。

【重要规则】
所有推荐店铺 必须 从下面的 商家池子 里选择，绝对不能出现池子以外的店！

=== 商家池子 ===
{shop_pool_str}
===============

用户画像：
{profile}

用户不喜欢的店（不要再推荐）：
{history_reject}

你的任务：
1. 根据用户当前需求推荐 3 个外卖
2. 必须从上面商家池子里选
3. 要符合用户画像
4. 要避免推荐用户已经拒绝过的店
5. 每条推荐包含：店名 + 推荐理由
"""
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    return response.choices[0].message.content

# ===== 主对话循环 =====
def chat():
    profile = load_profile()
    reject_history = []

    print("🍔 外卖推荐助手已启动！")
    print("✅ 已加载商家池：nearby_shops.json（共50+家真实店铺）")
    print("👉 你可以说：想吃辣的 / 想吃面 / 想吃新店 / 不想吃米饭")

    while True:
        user_input = input("\n你：")

        if user_input == "退出":
            break

        result = recommend(user_input, profile, reject_history)

        print("\n🤖 推荐：")
        print(result)

        feedback = input("\n👉 满意吗？（满意 / 不满意 / 说新需求）:")

        if feedback == "满意":
            print("🎉 祝你用餐愉快！")
            break
        elif feedback == "不满意":
            reject_history.append(result)
        else:
            user_input = feedback

if __name__ == "__main__":
    chat()