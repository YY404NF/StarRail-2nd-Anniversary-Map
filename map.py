import csv
import os
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageEnhance


def create_circular_avatar(source_img, size):
    """创建圆形头像
    :param source_img: PIL.Image对象，原始头像
    :param size: 头像尺寸
    :return: 圆形头像的PIL.Image对象
    """
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    circular_img = Image.new("RGBA", (size, size))
    circular_img.paste(source_img, (0, 0), mask=mask)
    return circular_img


def add_border(circular_img, border_size):
    """添加圆形边框
    :param circular_img: PIL.Image对象，圆形头像
    :param border_size: 边框宽度（像素）
    :return: 带边框头像的PIL.Image对象
    """
    bordered_size = circular_img.width + 2 * border_size
    bordered_img = Image.new("RGBA", (bordered_size, bordered_size), (0, 0, 0, 0))

    draw = ImageDraw.Draw(bordered_img)
    draw.ellipse(
        (0, 0, bordered_size, bordered_size),
        fill="white",
        outline="white"
    )

    bordered_img.alpha_composite(
        circular_img,
        dest=(border_size, border_size)
    )
    return bordered_img


def fetch_avatar(qq_number):
    """获取头像（优先使用缓存）
    :param qq_number: QQ号码
    :return: PIL.Image对象
    """
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    avatar_path = os.path.join(cache_dir, f"{qq_number}.png")

    if os.path.exists(avatar_path):
        return Image.open(avatar_path).convert("RGBA")

    # 下载并缓存头像
    url = f"https://q1.qlogo.cn/g?b=qq&nk={qq_number}&s=640"
    response = requests.get(url)
    response.raise_for_status()

    avatar = Image.open(BytesIO(response.content)).convert("RGBA")
    avatar.save(avatar_path)
    return avatar


def process_avatar(qq_number, avatar_size=200, border=10):
    """处理头像生成最终效果
    :param qq_number: QQ号码
    :param avatar_size: 头像尺寸
    :param border: 边框宽度
    :return: 处理好的PIL.Image对象
    """
    # 获取原始头像（自动处理缓存）
    avatar = fetch_avatar(qq_number)
    # 调整尺寸
    avatar = avatar.resize((avatar_size, avatar_size))
    # 生成圆形头像
    circular = create_circular_avatar(avatar, avatar_size)
    # 添加边框
    return add_border(circular, border)


def load_map_background(path):
    """加载并处理地图背景
    :param path: 背景图片路径
    :return: PIL.Image对象
    """
    map_img = Image.open(path).convert("RGBA")
    return ImageEnhance.Brightness(map_img).enhance(0.7)


def read_position_data(csv_path):
    """读取坐标数据
    :param csv_path: CSV文件路径
    :return: 包含(QQ号, X坐标, Y坐标)的列表
    """
    data = []
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            data.append((row[0], int(row[1]), int(row[2])))
    return data


def main():
    # 初始化地图
    map_img = load_map_background("background.png")

    # 读取坐标数据
    positions = read_position_data("data.csv")

    # 处理每个头像
    for qq, x, y in positions:
        avatar_img = process_avatar(qq)
        # 计算粘贴位置（居中）
        position = (
            x - avatar_img.width // 2,
            y - avatar_img.height // 2
        )
        map_img.paste(avatar_img, position, avatar_img)

    # 保存并显示结果
    map_img.save("output.png")
    map_img.show()


if __name__ == "__main__":
    main()