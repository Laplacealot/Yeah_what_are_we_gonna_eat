import base64
import json
import re
from zhipuai import ZhipuAI
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))


# 把图片转 base64（GLM-4V 必须这样传）
def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_order(image_path):
    base64_image = image_to_base64(image_path)

    response = client.chat.completions.create(
        model="glm-4v",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
                        请从这张外卖订单截图中提取订单信息，并严格按照以下JSON格式返回：
                        [
                            {
                                "店名": "xxx",
                                "菜品名称": "xxx",
                                "菜品口味": "xxx",
                                "食物类别": "xxx",
                                "实付款": "xx元",
                                "状态": "已完成"
                            }
                        ]
                        要求：
                        1. 只返回JSON数组，不要任何解释
                        2. 必须使用中文字段名（不要翻译成英文,如果原文是英文不需要翻译）
                        3. 所有标点必须是英文标点（, : "）
                        4. 如果识别不到字段，填“未知”
                        5. 只保留“已完成”的订单
                        6.菜品口味不要只看文字标注，需要根据【菜品名称、食材、菜系、品类】综合推理判断，口味严格分类为：辣口 / 咸口 / 甜口 / 清淡 / 酸甜 五类，
                        7.推理规则：
                        - 包含麻辣/香辣/藤椒/剁椒/火锅香辣锅底 → 辣口
                        - 中式炒菜、盖饭、卤肉、快餐正餐 → 咸口
                        - 奶茶、蛋糕、甜品、果汁、糖水 → 甜口
                        - 清汤、粥、轻食、蒸菜、养生餐 → 清淡
                        - 糖醋里脊、酸甜炸鸡、柠檬风味 → 酸甜
                        """
                                
                                
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )
    return response.choices[0].message.content


def clean_json_string(text):
    # 去掉 markdown 包裹
    text = re.sub(r"```json|```", "", text)

    # 替换中文标点
    text = text.replace("，", ",") \
               .replace("：", ":") \
               .replace("“", "\"") \
               .replace("”", "\"")

    # 去掉非法字符（比如奇怪的符号）
    text = re.sub(r"[^\x00-\x7F\u4e00-\u9fa5\[\]\{\}:,.\"]", "", text)

    return text.strip()

def save_to_orders(new_order):
    file_path = "orders.json"

    # 如果文件不存在，创建一个空列表
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f)

    # 读取已有数据
    with open(file_path, "r", encoding="utf-8") as f:
        orders = json.load(f)

    # 添加新订单
    orders.append(new_order)

    # 写回文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 自动读取所有分割后的图片：orderlist_part_0.jpg, 1, 2...
    image_files = [f for f in os.listdir() if f.startswith("orderlist_part_") and f.endswith(".jpg")]
    image_files.sort()  # 按顺序读取 0,1,2...

    if not image_files:
        print("❌ 没有找到分割后的订单图片")
        exit()

    # 遍历所有图片
    for img_file in image_files:
        print(f"\n📷 正在处理：{img_file}")
        result = analyze_order(img_file)
        print("模型原始输出：", result)

    # 尝试解析 JSON
    cleaned = clean_json_string(result)

    try:
        order_data = json.loads(cleaned)
    except Exception as e:
        print("❌ JSON解析失败：", e)
        print(cleaned)
        exit()

    # 逐条保存
    if isinstance(order_data, list):
        for order in order_data:
            save_to_orders(order)
    else:
        save_to_orders(order_data)

    print("✅ 已保存到 orders.json")