from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import tkinter.filedialog
import os

OUTPUT_IMAGE_WIDTH = 1200
OUTPUT_IMAGE_HEIGHT = 630

DEFAULT_BACKGROUND_COLOR = "#000000"

TEXT_FONT_PATH = "C:/Windows/Fonts/BIZ-UDGOTHICR.ttc"  # フォント設定（BIZ UDPゴシック）
LINE_SPACING_RATIO = 1.4  # 行間の広さを決める比率

TITLE_FONT_SIZE = 42
TITLE_TEXT_COLOR = "white"
TITLE_OUTLINE_COLOR = "black"

QUESTION_FONT_SIZE = 36
QUESTION_TEXT_COLOR = "white"
QUESTION_OUTLINE_COLOR = "black"

ANSWER_FONT_SIZE = 36
ANSWER_TEXT_COLOR = "yellow"
ANSWER_OUTLINE_COLOR = "black"


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


def draw_multiline(
    draw,
    text,
    font,
    area_top,
    area_height,
    x_margin,
    max_width,
    fill,
    outline_fill=None,
):
    lines = wrap_text_japanese(text, font, max_width, draw)

    base_line_height = font.getbbox("あ")[3]
    line_spacing = int(base_line_height * LINE_SPACING_RATIO)
    total_text_height = len(lines) * line_spacing

    y_start = area_top + (area_height - total_text_height) // 2

    for i, line in enumerate(lines):
        y = y_start + i * line_spacing
        x = x_margin

        # ===== 輪郭線を描画（周囲8方向）=====
        if outline_fill:
            offsets = [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
                (-1, -1),
                (-1, 1),
                (1, -1),
                (1, 1),
            ]
            for dx, dy in offsets:
                draw.text((x + dx, y + dy), line, font=font, fill=outline_fill)

        # ===== メインの文字を描画 =====
        draw.text((x, y), line, font=font, fill=fill)


def create_image(
    title,
    question,
    answer,
    output_path,
    background_image_path=None,
    background_color=DEFAULT_BACKGROUND_COLOR,
):
    width, height = OUTPUT_IMAGE_WIDTH, OUTPUT_IMAGE_HEIGHT

    # 背景画像 or 背景色の処理
    if background_image_path:
        background = Image.open(background_image_path).convert("RGB")
        background = background.resize((width, height))
    else:
        # 背景色が指定されていれば使い、なければ黒
        background = Image.new(
            "RGB", (width, height), color=background_color or DEFAULT_BACKGROUND_COLOR
        )

    draw = ImageDraw.Draw(background)

    # 領域高さの設定
    header_height = int(height * 0.05)
    title_height = int(height * 0.20)
    question_height = int(height * 0.50)
    answer_height = int(height * 0.20)
    footer_height = int(height * 0.05)

    font_path = TEXT_FONT_PATH
    font_title = ImageFont.truetype(font_path, TITLE_FONT_SIZE)
    font_question = ImageFont.truetype(font_path, QUESTION_FONT_SIZE)
    font_answer = ImageFont.truetype(font_path, ANSWER_FONT_SIZE)

    x_margin = 30
    max_text_width = width - x_margin * 2

    # ===== タイトル =====
    draw_multiline(
        draw,
        title,
        font_title,
        header_height,
        title_height,
        x_margin,
        max_text_width,
        fill=TITLE_TEXT_COLOR,
        outline_fill=TITLE_OUTLINE_COLOR,
    )

    # ===== 問題 =====
    draw_multiline(
        draw,
        question,
        font_question,
        header_height + title_height,
        question_height,
        x_margin,
        max_text_width,
        fill=QUESTION_TEXT_COLOR,
        outline_fill=QUESTION_OUTLINE_COLOR,
    )

    # ===== 答え =====
    draw_multiline(
        draw,
        f"Ans. : {answer}",
        font_answer,
        header_height + title_height + question_height,
        answer_height,
        x_margin,
        max_text_width,
        fill=ANSWER_TEXT_COLOR,
        outline_fill=ANSWER_OUTLINE_COLOR,
    )

    background.save(output_path)


def main():
    excel_file_name = tkinter.filedialog.askopenfilename(
        filetypes=[("Excelファイル", "*.xlsx")]
    )
    image_file_name = tkinter.filedialog.askopenfilename(
        filetypes=[("背景画像ファイル", "*.jpg;*.jpeg;*.png")]
    )

    base_dir = os.getcwd()

    df = pd.read_excel(excel_file_name)
    df["ファイル名接頭辞"] = df["ファイル名接頭辞"].fillna("").astype(str)

    for index, row in df.iterrows():
        ラウンド = row["ラウンド"]
        出題順 = int(row["出題順"])
        問題文 = row["問題文"]
        答え = row["答え"]
        フォルダ名 = str(row["フォルダ名"])
        ファイル名接頭辞 = str(row["ファイル名接頭辞"])

        full_path = os.path.join(base_dir, フォルダ名)

        if not os.path.exists(full_path):
            os.makedirs(full_path)

        create_image(
            f"{ラウンド} {出題順}問目",
            問題文,
            答え,
            output_path=f"{フォルダ名}/{ファイル名接頭辞}{str(出題順).zfill(3)}.png",
            background_image_path=image_file_name,
            background_color=DEFAULT_BACKGROUND_COLOR,
        )


if __name__ == "__main__":
    main()
