import base64
import json
import os
from zhipuai import ZhipuAI
from dotenv import load_dotenv

# 加载环境变量（你自己写的，完全一致）
load_dotenv()

# 智谱客户端（你自己的代码）
client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))

# 图片转 base64（你自己写的）
def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# 单张图片解析（智谱 GLM-4V 官方格式）
def parse_shops(image_path):
    base64_image = image_to_base64(image_path)

    prompt = """
    你是一个外卖截图解析助手。
    请提取图片里所有店铺信息，严格返回JSON数组，不要任何多余文字、markdown、解释。
    格式：
    [
        {"店名":"","评分":"","月售":"","配送费":"","起送价":"","距离":""}
    ]
    """

    response = client.chat.completions.create(
        model="glm-4v",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]
    )
    return response.choices[0].message.content

# 清理JSON
def clean_json_string(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

# ===================== 你要的 批量解析函数 =====================
def parse_multiple_images():
    all_shops = []

    # 遍历所有 shop_part 开头的图片
    for file in os.listdir():
        if file.startswith("shop_part") and file.endswith(".jpg"):
            print(f"正在解析 {file}")

            try:
                result = parse_shops(file)
                cleaned = clean_json_string(result)
                data = json.loads(cleaned)

                if isinstance(data, list):
                    all_shops.extend(data)
            except Exception as e:
                print(f"❌ 解析失败，跳过：{e}")

    # 按店名去重
    unique = {}
    for shop in all_shops:
        name = shop.get("店名")
        if name:
            unique[name] = shop

    final_shops = list(unique.values())

    # 保存JSON
    with open("nearby_shops.json", "w", encoding="utf-8") as f:
        json.dump(final_shops, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成！共保存 {len(final_shops)} 个商家")

# ===================== 运行 =====================
if __name__ == "__main__":
    parse_multiple_images()