import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# Constants
DPI = 300
STICKER_WIDTH_MM = 38
STICKER_HEIGHT_MM = 21
NUM_COLUMNS = 5
NUM_ROWS = 13
FONT_SIZE = 45
LINE_SPACING = 2

# Derived values
STICKER_WIDTH = int((STICKER_WIDTH_MM / 25.4) * DPI)
STICKER_HEIGHT = int((STICKER_HEIGHT_MM / 25.4) * DPI)
A4_WIDTH_PX = int((210 / 25.4) * DPI)
A4_HEIGHT_PX = int((297 / 25.4) * DPI)
MAX_STICKERS_ON_PAGE = NUM_COLUMNS * NUM_ROWS


# Load font
def load_font():
    try:
        return ImageFont.truetype("fonts/arialbd.ttf", FONT_SIZE)
    except:
        return ImageFont.load_default()

font = load_font()

# Streamlit UI
st.title("Sticker Sheet Generator")

with st.form("sticker_form"):
    date = st.text_input("Date (e.g., 01-07-2024)")
    invoice_no = st.text_input("Invoice Number (e.g., INV-123)")
    supplier = st.text_input("Supplier Name")

    num_items = st.number_input("Number of Different Items", min_value=1, step=1)
    
    item_pieces = {}
    total_pieces = 0
    for i in range(1, num_items + 1):
        pieces = st.number_input(f"Number of pieces for Item {i}", min_value=1, step=1, key=f"item_{i}")
        item_pieces[i] = pieces
        total_pieces += pieces

    submitted = st.form_submit_button("Generate Stickers")

if submitted:
    # Create sticker sheet image
    sticker_sheet = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), "white")
    draw = ImageDraw.Draw(sticker_sheet)
    x_margin = (A4_WIDTH_PX - (STICKER_WIDTH * NUM_COLUMNS)) // 2
    y_margin = (A4_HEIGHT_PX - (STICKER_HEIGHT * NUM_ROWS)) // 2

    sticker_index = 0
    for item_num, num_pieces in item_pieces.items():
        for piece_num in range(1, num_pieces + 1):
            if sticker_index >= MAX_STICKERS_ON_PAGE:
                break

            row = sticker_index // NUM_COLUMNS
            col = sticker_index % NUM_COLUMNS
            x_pos = x_margin + col * STICKER_WIDTH
            y_pos = y_margin + row * STICKER_HEIGHT

            draw.rectangle(
                [x_pos, y_pos, x_pos + STICKER_WIDTH, y_pos + STICKER_HEIGHT],
                outline="black",
                width=2
            )

            lines = [
                f"Date: {date}".upper(),
                f"Invoice: {invoice_no}".upper(),
                f"Supplier : {supplier}".upper(),
                f"Item: {item_num}".upper(),
                f"Piece: {piece_num}/{num_pieces}".upper()
            ]

            total_text_height = len(lines) * (FONT_SIZE + LINE_SPACING) - LINE_SPACING
            y_text_start = max(y_pos + 10, y_pos + (STICKER_HEIGHT - total_text_height) // 2)

            for i, line in enumerate(lines):
                draw.text((x_pos + 10, y_text_start + i * (FONT_SIZE + LINE_SPACING)), line, font=font, fill="black")

            sticker_index += 1

    # Save to BytesIO
    img_buffer = io.BytesIO()
    sticker_sheet.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    # Display preview and download button
    st.image(sticker_sheet, caption="Sticker Sheet Preview", use_column_width=True)
    st.download_button(
        label="Download Sticker Sheet",
        data=img_buffer,
        file_name="stickers_page_1.png",
        mime="image/png"
    )
