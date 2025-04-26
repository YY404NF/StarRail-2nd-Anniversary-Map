import csv
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageEnhance


def create_circular_avatar(source_img, size):
    """创建圆形头像"""
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    circular_img = Image.new("RGBA", (size, size))
    circular_img.paste(source_img, (0, 0), mask=mask)
    return circular_img


def add_border(circular_img, border_size):
    """添加圆形边框"""
    bordered_size = circular_img.width + 2 * border_size
    bordered_img = Image.new("RGBA", (bordered_size, bordered_size), (0, 0, 0, 0))

    # 绘制白色边框
    draw = ImageDraw.Draw(bordered_img)
    draw.ellipse(
        (0, 0, bordered_size, bordered_size),
        fill="white",
        outline="white"
    )

    # 叠加原头像
    bordered_img.alpha_composite(
        circular_img,
        dest=(border_size, border_size)
    )
    return bordered_img

def get_circular_avatar(qq_number, avatar_size=200, border=10, **shadow_kwargs):
    """生成带边框的头像"""
    # 下载原始头像
    url = f"https://q1.qlogo.cn/g?b=qq&nk={qq_number}&s=640"
    response = requests.get(url)
    avatar = Image.open(BytesIO(response.content)).convert("RGBA")
    avatar = avatar.resize((avatar_size, avatar_size))

    circular = create_circular_avatar(avatar, avatar_size)
    final_img = add_border(circular, border)

    return final_img


# 主程序流程
if __name__ == "__main__":
    # 加载地图
    map_img = Image.open("background.png").convert("RGBA")
    map_img = ImageEnhance.Brightness(map_img).enhance(0.7)

    # 读取数据
    qq_data = []
    with open("data.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            qq_data.append((row[0], int(row[1]), int(row[2])))

    # 渲染所有头像
    for qq, x, y in qq_data:
        avatar_img = get_circular_avatar(
            qq,
            avatar_size=200,
            border=10,
            shadow_size=20,
            shadow_blur=10,
            shadow_opacity=80
        )
        # 计算居中坐标（自动处理阴影偏移）
        map_img.paste(
            avatar_img,
            (x - avatar_img.width // 2, y - avatar_img.height // 2),
            avatar_img
        )

    map_img.save("output.png")
    map_img.show()