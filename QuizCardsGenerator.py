import os
import sys
import json
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from tkinter import filedialog

# ======================
# 設定読込
# ======================
CONFIG_PATH = "config.json"

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

CONFIG = load_config(CONFIG_PATH)

# ======================
# ユーティリティ関数
# ======================
def wrap_text_japanese(text, font, max_width, draw):
    lines = []
    line = ""
    for char in text:
        test_line = line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = char
    if line:
        lines.append(line)
    return lines


def draw_multiline(draw, text, font, area_top, area_height, x_margin, max_width, fill, outline_fill=None):
    line_spacing_ratio = CONFIG["layout"]["line_spacing_ratio"]
    lines = wrap_text_japanese(text, font, max_width, draw)
    base_line_height = font.getbbox("あ")[3]
    line_spacing = int(base_line_height * line_spacing_ratio)
    total_text_height = len(lines) * line_spacing
    y_start = area_top + (area_height - total_text_height) // 2

    for i, line in enumerate(lines):
        y = y_start + i * line_spacing
        x = x_margin
        if outline_fill:
            offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dx, dy in offsets:
                draw.text((x + dx, y + dy), line, font=font, fill=outline_fill)
        draw.text((x, y), line, font=font, fill=fill)


# ======================
# 画像生成関数
# ======================
def create_image(title, question, answer, background_image_path=None,
                 brightness=None, contrast=None, blur=None):
    width = CONFIG["image"]["width"]
    height = CONFIG["image"]["height"]
    background_color = CONFIG["image"].get("background_color", "#000000")

    brightness_factor = brightness if brightness is not None else CONFIG["image"].get("brightness", 1.0)
    contrast_factor = contrast if contrast is not None else CONFIG["image"].get("contrast", 1.0)
    blur_radius = blur if blur is not None else CONFIG["image"].get("blur", 0)

    if background_image_path:
        background = Image.open(background_image_path).convert("RGB").resize((width, height))
        if brightness_factor != 1.0:
            background = ImageEnhance.Brightness(background).enhance(brightness_factor)
        if contrast_factor != 1.0:
            background = ImageEnhance.Contrast(background).enhance(contrast_factor)
        if blur_radius > 0:
            background = background.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    else:
        background = Image.new("RGB", (width, height), color=background_color)

    draw = ImageDraw.Draw(background)

    header_height = int(height * 0.05)
    title_height = int(height * 0.20)
    question_height = int(height * 0.50)
    answer_height = int(height * 0.20)

    font_path = CONFIG["font"]["path"]
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"フォントファイルが見つかりません: {font_path}")

    font_title = ImageFont.truetype(font_path, CONFIG["font"]["title_size"])
    font_question = ImageFont.truetype(font_path, CONFIG["font"]["question_size"])
    font_answer = ImageFont.truetype(font_path, CONFIG["font"]["answer_size"])

    x_margin = CONFIG["layout"]["x_margin"]
    max_text_width = width - x_margin * 2

    draw_multiline(draw, title, font_title, header_height, title_height, x_margin, max_text_width,
                   CONFIG["color"]["title_text"], CONFIG["color"]["title_outline"])
    draw_multiline(draw, question, font_question, header_height + title_height, question_height, x_margin, max_text_width,
                   CONFIG["color"]["question_text"], CONFIG["color"]["question_outline"])
    draw_multiline(draw, f"Ans. : {answer}", font_answer, header_height + title_height + question_height,
                   answer_height, x_margin, max_text_width, CONFIG["color"]["answer_text"], CONFIG["color"]["answer_outline"])

    return background


# ======================
# メイン処理部
# ======================
def select_excel_file():
    return filedialog.askopenfilename(filetypes=[("Excelファイル", "*.xlsx")])


def select_background_image():
    return filedialog.askopenfilename(filetypes=[("背景画像ファイル", ("*.jpg", "*.jpeg", "*.png"))])


def process_excel_data(df, background_image_path):
    df["ファイル名接頭辞"] = df["ファイル名接頭辞"].fillna("").astype(str)
    base_dir = os.getcwd()

    for _, row in df.iterrows():
        try:
            round_title = row["ラウンド"]
            order = int(row["出題順"])
            question = row["問題文"]
            answer = row["答え"]
            folder = str(row["フォルダ名"])
            prefix = str(row["ファイル名接頭辞"])

            output_dir = os.path.join(base_dir, folder)
            os.makedirs(output_dir, exist_ok=True)

            filename = f"{prefix}{str(order).zfill(3)}.png"
            output_path = os.path.join(output_dir, filename)

            image = create_image(f"{round_title} {order}問目", question, answer, background_image_path)
            image.save(output_path)
        except Exception as e:
            print(f"{order}問目の処理中にエラー: {e}")


# ======================
# エントリーポイント
# ======================
def main():
    import argparse
    parser = argparse.ArgumentParser(description="画像生成モード")
    parser.add_argument("mode", nargs="?", default="normal", choices=["normal", "test"], help="モード選択: 'normal' or 'test'")
    parser.add_argument("--brightness", type=float, help="明るさ（1.0 = デフォルト）")
    parser.add_argument("--contrast", type=float, help="コントラスト（1.0 = デフォルト）")
    parser.add_argument("--blur", type=float, help="ぼかし半径（0 = なし）")
    parser.add_argument("--background", type=str, help="背景画像パス（省略時はダイアログ）")
    args = parser.parse_args()

    if args.mode == "test":
        background_path = args.background or select_background_image()
        if not background_path:
            print("背景画像が選択されませんでした。")
            return

        title = CONFIG["test"]["title"]
        question = CONFIG["test"]["question"]
        answer = CONFIG["test"]["answer"]

        image = create_image(title, question, answer, background_path,
                             brightness=args.brightness, contrast=args.contrast, blur=args.blur)
        image.show()
        return

    # 通常モード
    excel_path = select_excel_file()
    if not excel_path:
        print("Excelファイルが選択されませんでした。")
        return

    background_path = select_background_image()
    if not background_path:
        print("背景画像が選択されませんでした。")
        return

    try:
        df = pd.read_excel(excel_path)
        process_excel_data(df, background_path)
    except Exception as e:
        print(f"全体処理中にエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
