import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# App Title
st.title("Sticker Sheet Generator")

# Sidebar Inputs
st.sidebar.header("Sticker Details")

date = st.sidebar.text_input("Date (e.g., 01-07-2024):", "01-07-2024")
invoice_no = st.sidebar.text_input("Invoice Number (e.g., INV-123):", "INV-123")
supplier = st.sidebar.text_input("Supplier Name:", "Example Supplier")

num_different_items = st.sidebar.number_input("Number of Different Items:", min_value=1, value=2)
item_pieces = {}
total_pieces = 0

st.sidebar.markdown("### Number of Pieces for Each Item:")
for item_num in range(1, num_different_items + 1):
    pieces = st.sidebar.number_input(f"Item {item_num} pieces:", min_value=1, value=2, key=f"item_{item_num}")
    item_pieces[item_num] = pieces
    total_pieces += pieces

num_columns = st.sidebar.number_input("Number of Stickers per Row:", min_value=1, value=4)

# Sticker Settings
STICKER_WIDTH, STICKER_HEIGHT = 400, 200  # Size of each sticker
FONT_SIZE = 25

# Calculate number of rows and total image dimensions
num_rows = (total_pieces + num_columns - 1) // num_columns
total_width = STICKER_WIDTH * num_columns
total_height = STICKER_HEIGHT * num_rows

# Button to Generate Stickers
if st.sidebar.button("Generate Stickers"):
    # Create a blank image
    sticker_sheet = Image.new("RGB", (total_width, total_height), "white")
    draw = ImageDraw.Draw(sticker_sheet)

    # Load font (default if Arial not found)
    try:
        font = ImageFont.truetype("arial.ttf", FONT_SIZE)
    except:
        font = ImageFont.load_default()

    # Generate Stickers
    current_piece_index = 0
    for item_num, num_pieces in item_pieces.items():
        for piece_num in range(1, num_pieces + 1):
            row = current_piece_index // num_columns
            col = current_piece_index % num_columns
            x_position = col * STICKER_WIDTH
            y_position = row * STICKER_HEIGHT

            # Draw sticker border
            draw.rectangle(
                [x_position, y_position, x_position + STICKER_WIDTH, y_position + STICKER_HEIGHT],
                outline="black",
                width=2
            )

            # Text to write on sticker
            text_lines = [
                f"Date: {date}",
                f"Invoice: {invoice_no}",
                f"Supplier: {supplier}",
                f"Item: {item_num}",
                f"Piece: {piece_num}/{num_pieces}"
            ]

            total_text_height = len(text_lines) * (FONT_SIZE + 10)
            start_y_text = y_position + (STICKER_HEIGHT - total_text_height) // 2

            for i, line in enumerate(text_lines):
                text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:]
                x_text = x_position + (STICKER_WIDTH - text_width) // 2
                y_text = start_y_text + (i * (FONT_SIZE + 10))
                draw.text((x_text, y_text), line, font=font, fill="black")

            current_piece_index += 1

    # Convert image to bytes for display and download
    img_buffer = io.BytesIO()
    sticker_sheet.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # Show image in app
    st.image(img_buffer, caption=f"{total_pieces} Stickers Generated", use_column_width=True)

    # Download button
    b64 = base64.b64encode(img_buffer.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{b64}" download="stickers.png">📥 Download Sticker Sheet</a>'
    st.markdown(href, unsafe_allow_html=True)
