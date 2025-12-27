from PIL import Image, ImageDraw, ImageFont
import math

def create_book_cover():
    # 创建封面尺寸 (800x1200 像素，适合书籍封面比例)
    width, height = 800, 1200
    img = Image.new('RGB', (width, height), '#ffffff')
    draw = ImageDraw.Draw(img)

    # 创建渐变背景 (深蓝到浅蓝)
    for y in range(height):
        # 从深蓝 (#1a237e) 到浅蓝 (#42a5f5) 的渐变
        r = int(26 + (66 - 26) * (y / height))
        g = int(35 + (165 - 35) * (y / height))
        b = int(126 + (245 - 126) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 添加科技网格背景
    grid_color = (255, 255, 255, 30)
    for x in range(0, width, 50):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 50):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # 绘制数据流可视化效果
    def draw_data_flow():
        # 绘制抽象的数据流线条
        flow_color = (255, 255, 255, 150)
        for i in range(5):
            y_offset = 200 + i * 150
            points = []
            for x in range(0, width, 20):
                y = y_offset + 30 * math.sin(x * 0.02 + i) + 20 * math.sin(x * 0.05)
                points.append((x, y))
            if len(points) > 1:
                draw.line(points, fill=flow_color, width=2)

    draw_data_flow()

    # 绘制AI大脑图标 (简化版)
    def draw_ai_brain(x, y, size=80):
        brain_color = (255, 255, 255, 200)
        # 绘制大脑轮廓
        brain_points = [
            (x, y), (x+size*0.3, y-size*0.2), (x+size*0.7, y-size*0.3),
            (x+size, y), (x+size*0.7, y+size*0.3), (x+size*0.3, y+size*0.2)
        ]
        draw.polygon(brain_points, fill=brain_color)

        # 添加神经网络连接线
        network_color = (100, 200, 255, 150)
        for i in range(8):
            angle = i * math.pi / 4
            end_x = x + size * 0.5 * math.cos(angle)
            end_y = y + size * 0.3 * math.sin(angle)
            draw.line([(x + size*0.5, y), (end_x, end_y)], fill=network_color, width=1)

    draw_ai_brain(350, 300)

    # 绘制测试齿轮图标
    def draw_test_gear(x, y, size=60):
        gear_color = (255, 200, 100, 200)
        # 绘制齿轮主体
        draw.ellipse([x-size/2, y-size/2, x+size/2, y+size/2], fill=gear_color)

        # 绘制齿轮齿
        for i in range(8):
            angle = i * math.pi / 4
            inner_x = x + (size*0.3) * math.cos(angle)
            inner_y = y + (size*0.3) * math.sin(angle)
            outer_x = x + (size*0.5) * math.cos(angle)
            outer_y = y + (size*0.5) * math.sin(angle)
            draw.line([(inner_x, inner_y), (outer_x, outer_y)], fill=gear_color, width=3)

        # 绘制中心孔
        draw.ellipse([x-size/6, y-size/6, x+size/6, y+size/6], fill=(50, 50, 50))

    draw_test_gear(450, 400)

    # 绘制大数据图标 (数据块堆叠)
    def draw_data_blocks(x, y):
        block_color = (100, 200, 150, 180)
        for i in range(4):
            for j in range(3):
                bx = x + i * 25
                by = y + j * 25
                draw.rectangle([bx, by, bx+20, by+20], fill=block_color, outline=(255, 255, 255, 100))

    draw_data_blocks(300, 500)

    # 添加书名
    title_lines = ["大数据全栈测试", "从理论到实战"]
    title_y = 100

    for line in title_lines:
        # 计算文字居中位置
        bbox = draw.textbbox((0, 0), line, font=None)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = title_y

        # 添加文字阴影效果
        shadow_offset = 2
        draw.text((x + shadow_offset, y + shadow_offset), line, fill=(0, 0, 0, 100), font=None)

        # 绘制主要文字
        draw.text((x, y), line, fill=(255, 255, 255), font=None)

        title_y += 50

    # 添加技术标签
    tech_tags = [
        "大数据", "AI驱动", "云计算", "DevOps",
        "数据质量", "可观测性", "全栈测试", "智能化"
    ]

    # 技术标签位置和颜色
    tag_positions = [
        (150, 650), (250, 680), (350, 650), (450, 680),
        (150, 720), (250, 750), (350, 720), (450, 750)
    ]

    tag_colors = [
        (255, 100, 100), (100, 200, 255), (150, 255, 150), (255, 200, 100),
        (200, 150, 255), (255, 150, 200), (150, 255, 200), (255, 255, 150)
    ]

    # 绘制技术标签
    for i, (tag, pos, color) in enumerate(zip(tech_tags, tag_positions, tag_colors)):
        # 标签背景
        text_bbox = draw.textbbox(pos, tag, font=None)
        padding = 8
        draw.rectangle([
            text_bbox[0]-padding, text_bbox[1]-padding,
            text_bbox[2]+padding, text_bbox[3]+padding
        ], fill=color + (180,), outline=color + (255,))

        # 标签文字
        draw.text(pos, tag, fill=(0, 0, 0), font=None)

    # 保存图片
    img.save('book_cover_design_v2.png', 'PNG')
    print("新封面设计已生成: book_cover_design_v2.png")

if __name__ == "__main__":
    create_book_cover()