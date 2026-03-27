from PIL import Image, ImageDraw, ImageFont
import os

# =========================
# 1. 图片目录和输出文件
# =========================
chart_dir = "charts"
output_file = "ecommerce_dashboard.png"

# =========================
# 2. 需要拼接的图片顺序
# 2 行 4 列
# =========================
image_files = [
    "gmv_trend.png",
    "dau_trend.png",
    "new_user_trend.png",
    "pay_conversion_trend.png",
    "funnel_chart.png",
    "product_sales_qty_top10.png",
    "product_sales_amount_top10.png",
    "channel_orders.png"
]

# =========================
# 3. 标题文字
# =========================
dashboard_title = "电商用户行为分析看板"

# =========================
# 4. 基础参数
# =========================
padding = 20          # 图之间的间距
title_height = 80     # 顶部标题区域高度
bg_color = "white"

# =========================
# 5. 读取图片
# =========================
images = []
for file_name in image_files:
    file_path = os.path.join(chart_dir, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到图片文件: {file_path}")
    img = Image.open(file_path).convert("RGB")
    images.append(img)

# =========================
# 6. 统一缩放尺寸
# 每张图统一缩放到相同大小
# =========================
target_width = 700
target_height = 400

resized_images = []
for img in images:
    resized = img.resize((target_width, target_height))
    resized_images.append(resized)

# =========================
# 7. 画布尺寸：2 行 4 列
# =========================
cols = 4
rows = 2

canvas_width = cols * target_width + (cols + 1) * padding
canvas_height = rows * target_height + (rows + 1) * padding + title_height

canvas = Image.new("RGB", (canvas_width, canvas_height), bg_color)
draw = ImageDraw.Draw(canvas)

# =========================
# 8. 处理标题字体
# Windows 常见中文字体路径
# 如果找不到，会退回默认字体
# =========================
font = None
font_paths = [
    "C:/Windows/Fonts/msyh.ttc",   # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf", # 黑体
    "C:/Windows/Fonts/simsun.ttc", # 宋体
]

for path in font_paths:
    if os.path.exists(path):
        font = ImageFont.truetype(path, 36)
        break

if font is None:
    font = ImageFont.load_default()

# =========================
# 9. 绘制总标题
# =========================
bbox = draw.textbbox((0, 0), dashboard_title, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

title_x = (canvas_width - text_width) // 2
title_y = (title_height - text_height) // 2
draw.text((title_x, title_y), dashboard_title, fill="black", font=font)

# =========================
# 10. 把 8 张图贴到画布上
# =========================
for idx, img in enumerate(resized_images):
    row = idx // cols
    col = idx % cols

    x = padding + col * (target_width + padding)
    y = title_height + padding + row * (target_height + padding)

    canvas.paste(img, (x, y))

# =========================
# 11. 保存结果
# =========================
canvas.save(output_file, quality=95)
print(f"总览看板已生成: {output_file}")