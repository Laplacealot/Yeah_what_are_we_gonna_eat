from PIL import Image

def split_image(image_path, output_prefix, height=1000):
    img = Image.open(image_path)
    width, total_height = img.size

    count = 0
    for i in range(0, total_height, height):
        box = (0, i, width, i + height)
        part = img.crop(box)

        # ⭐ 关键修复
        part = part.convert("RGB")

        part.save(f"{output_prefix}_{count}.jpg")
        count += 1

    print(f"✅ 切分完成，共 {count} 张")


if __name__ == "__main__":
    split_image("shop.jpg", "shop_part")