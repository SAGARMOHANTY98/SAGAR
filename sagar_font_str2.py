import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import os

def get_font(size):
    font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    return ImageFont.truetype(font_path, size)

def calculate_optimal_font_size(label_width, label_height, sample_text_lines):
    min_size = 8
    max_size = 30
    padding = 0.25
    available_height = label_height - 0.5 * padding

    best_size = min_size
    for size in range(min_size, max_size + 1):
        font = get_font(size)
        line_heights = []
        max_line_width = 0
        for line in sample_text_lines:
            bbox = font.getbbox(line)
            line_height = bbox[3] - bbox[1]
            line_width = bbox[2] - bbox[0]
            line_heights.append(line_height)
            max_line_width = max(max_line_width, line_width)

        total_text_height = sum(line_heights)
        if total_text_height <= available_height and max_line_width <= (label_width - 2 * padding):
            best_size = size
        else:
            break

    return best_size

def generate_labels(date, invoice_no, supplier, items_data):
    DPI = 300
    A4_WIDTH_MM, A4_HEIGHT_MM = 210, 297
    A4_WIDTH_PX = int(A4_WIDTH_MM / 25.4 * DPI)
    A4_HEIGHT_PX = int(A4_HEIGHT_MM / 25.4 * DPI)
    LABEL_WIDTH_MM, LABEL_HEIGHT_MM = 38, 21
    LABEL_WIDTH_PX = int(LABEL_WIDTH_MM / 25.4 * DPI)
    LABEL_HEIGHT_PX = int(LABEL_HEIGHT_MM / 25.4 * DPI)

    COLS, ROWS = 5, 13
    MAX_LABELS_PER_SHEET = COLS * ROWS

    MARGIN_LEFT_RIGHT_MM = 6
    MARGIN_TOP_BOTTOM_MM = 12
    V_SPACING_MM = 2

    MARGIN_LEFT_RIGHT_PX = int(MARGIN_LEFT_RIGHT_MM / 25.4 * DPI)
    MARGIN_TOP_BOTTOM_PX = int(MARGIN_TOP_BOTTOM_MM / 25.4 * DPI)
    v_spacing = int(V_SPACING_MM / 25.4 * DPI)

    available_width = A4_WIDTH_PX - (2 * MARGIN_LEFT_RIGHT_PX)
    available_height = A4_HEIGHT_PX - (2 * MARGIN_TOP_BOTTOM_PX)

    total_label_width = COLS * LABEL_WIDTH_PX
    total_label_height = ROWS * LABEL_HEIGHT_PX

    h_spacing = (available_width - total_label_width) // (COLS - 1)

    start_x = MARGIN_LEFT_RIGHT_PX
    start_y = MARGIN_TOP_BOTTOM_PX

    sample_lines = [
        f"DATE: {date}",
        f"INVOICE: {invoice_no}",
        f"SUPPLIER: {supplier[:12]}",
        "ITEM: 99",
        "PIECE: 999/999"
    ]

    font_size = calculate_optimal_font_size(LABEL_WIDTH_PX, LABEL_HEIGHT_PX, sample_lines)
    font = get_font(font_size)

    sheet_number = 1
    label_count = 0
    sheet = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), "white")
    draw = ImageDraw.Draw(sheet)

    saved_sheets = []
    total_labels = sum(items_data.values())

    for item_num, num_pieces in items_data.items():
        for piece_num in range(1, num_pieces + 1):
            if label_count >= MAX_LABELS_PER_SHEET:
                buffer = io.BytesIO()
                sheet.save(buffer, format="PNG", dpi=(DPI, DPI))
                buffer.seek(0)
                saved_sheets.append((f"Invoice_Labels_Sheet_{sheet_number}.png", buffer.read()))

                sheet_number += 1
                sheet = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), "white")
                draw = ImageDraw.Draw(sheet)
                label_count = 0

            col = label_count % COLS
            row = label_count // COLS

            x = start_x + col * (LABEL_WIDTH_PX + h_spacing)
            y = start_y + row * (LABEL_HEIGHT_PX + v_spacing)

            draw.rectangle(
                [x, y, x + LABEL_WIDTH_PX - 1, y + LABEL_HEIGHT_PX - 1],
                outline="black",
                width=1
            )

            supplier_short = supplier[:12]
            text_lines = [
                f"DATE: {date}",
                f"INVOICE: {invoice_no}",
                f"SUPPLIER: {supplier_short}",
                f"ITEM: {item_num}",
                f"PIECE: {piece_num}/{num_pieces}"
            ]

            padding = 6
            line_heights = []
            for line in text_lines:
                bbox = font.getbbox(line)
                line_heights.append(bbox[3] - bbox[1])

            total_text_height = sum(line_heights)
            available_label_height = LABEL_HEIGHT_PX - 2 * padding
            remaining_space = available_label_height - total_text_height

            if len(text_lines) > 1:
                line_spacing = int(remaining_space // (len(text_lines) - 1))
            else:
                line_spacing = 0

            current_y = y + padding
            for i, line in enumerate(text_lines):
                draw.text((x + padding, current_y), line, fill="black", font=font)
                current_y += line_heights[i] + line_spacing

            label_count += 1

    # Save last sheet
    buffer = io.BytesIO()
    sheet.save(buffer, format="PNG", dpi=(DPI, DPI))
    buffer.seek(0)
    saved_sheets.append((f"Invoice_Labels_Sheet_{sheet_number}.png", buffer.read()))

    return saved_sheets, font_size, total_labels, sheet_number

# Streamlit App  
st.title("🖨️ Invoice Label Generator")

date = st.text_input("Date", "01-07-2024")
invoice_no = st.text_input("Invoice Number", "INV-123")
supplier = st.text_input("Supplier Name")

num_items = st.number_input("Number of different items", min_value=1, max_value=20, value=1)
items_data = {}

for i in range(1, num_items + 1):
    pieces = st.number_input(f"Number of pieces for Item {i}", min_value=1, max_value=1000, value=1, key=f"item_{i}")
    items_data[i] = pieces

if st.button("Generate Labels"):
    with st.spinner("Generating labels..."):
        saved_sheets, font_size, total_labels, sheet_count = generate_labels(date, invoice_no, supplier, items_data)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for filename, data in saved_sheets:
                zip_file.writestr(filename, data)

        st.success(f"✅ Generated {total_labels} labels across {sheet_count} sheet(s) | Font Size: {font_size}pt")

        st.download_button(
            label="📥 Download All Label Sheets (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="Invoice_Labels.zip",
            mime="application/zip"
        )
