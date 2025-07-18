import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# --------- Wilton Weaver Theme CSS ---------
def set_wilton_theme():
    st.markdown("""
    <style>
    .stApp {
        background-color: #fdf5e6;
        background-image: repeating-linear-gradient(
            45deg,
            #f9f4ee,
            #f9f4ee 10px,
            #f3e8d8 10px,
            #f3e8d8 20px
        );
        background-size: cover;
        font-family: 'Segoe UI', sans-serif;
    }

    .sticker-header {
        color: #8B0000;
        text-align: center;
        font-size: 2.8rem;
        margin-bottom: 1.2rem;
        font-weight: bold;
        text-shadow: 1px 1px 2px #e6d3b3;
        letter-spacing: 1px;
    }

    .company-subheader {
        color: #444;
        text-align: center;
        font-size: 1.2rem;
        font-style: italic;
        margin-top: -10px;
        margin-bottom: 20px;
    }

    .sticker-form {
        background-color: #fff8f0;
        border-radius: 14px;
        padding: 2rem;
        border: 3px double #8B0000;
        box-shadow: 0 4px 12px rgba(139, 0, 0, 0.1);
        margin-bottom: 2rem;
    }

    .stTextInput>div>div>input, .stNumberInput input {
        border: 2px solid #DAA520 !important;
        border-radius: 8px !important;
        background-color: #fff;
        padding: 0.4rem;
    }

    .stButton>button {
        background-color: #8B0000 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: bold !important;
        border: 2px solid #B22222 !important;
        transition: 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #A52A2A !important;
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0,0,0,0.2);
    }

    .stImage>img {
        border: 3px solid #DAA520;
        border-radius: 10px;
        margin-top: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .stDownloadButton>button {
        background-color: #003366 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        margin-top: 0.5rem;
    }

    .stDownloadButton>button:hover {
        background-color: #001f4d !important;
    }

    h3, h4, h5 {
        color: #8B0000;
        border-bottom: 2px dotted #DAA520;
        padding-bottom: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# --------- Font Loader ---------
def get_font(size):
    return ImageFont.truetype("DejaVuSans-Bold.ttf", size)

# --------- Optimal Font Size ---------
def calculate_optimal_font_size(label_width, label_height, sample_text_lines):
    min_size, max_size = 8, 28
    padding = 0.25
    available_height = label_height - 0.5 * padding
    best_size = min_size
    for size in range(min_size, max_size + 1):
        font = get_font(size)
        line_heights, max_line_width = [], 0
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

# --------- Label Generation ---------
def generate_invoice_labels(date, invoice_no, supplier, items_data):
    DPI = 300
    A4_WIDTH_MM, A4_HEIGHT_MM = 210, 297
    LABEL_WIDTH_MM, LABEL_HEIGHT_MM = 37.02, 20.99
    COLS, ROWS = 5, 13
    MARGIN_LEFT_RIGHT_MM = 6
    MARGIN_TOP_BOTTOM_MM = 12
    H_SPACING_MM, V_SPACING_MM = 2, 0

    A4_WIDTH_PX = int(A4_WIDTH_MM / 25.4 * DPI)
    A4_HEIGHT_PX = int(A4_HEIGHT_MM / 25.4 * DPI)
    LABEL_WIDTH_PX = int(LABEL_WIDTH_MM / 25.4 * DPI)
    LABEL_HEIGHT_PX = int(LABEL_HEIGHT_MM / 25.4 * DPI)
    MARGIN_LEFT_RIGHT_PX = int(MARGIN_LEFT_RIGHT_MM / 25.4 * DPI)
    MARGIN_TOP_BOTTOM_PX = int(MARGIN_TOP_BOTTOM_MM / 25.4 * DPI)
    h_spacing = int(H_SPACING_MM / 25.4 * DPI)
    v_spacing = int(V_SPACING_MM / 25.4 * DPI)

    MAX_LABELS = COLS * ROWS
    start_x, start_y = MARGIN_LEFT_RIGHT_PX, MARGIN_TOP_BOTTOM_PX

    sample_lines = [
        f"DATE: {date}",
        f"INVOICE: {invoice_no}",
        f"SUPPLIER: {supplier}",
        "ITEM: 99",
        "PIECE: 999/999"
    ]
    font_size = calculate_optimal_font_size(LABEL_WIDTH_PX, LABEL_HEIGHT_PX, sample_lines)
    font = get_font(font_size)

    sheets, label_count, sheet_number = [], 0, 1
    sheet = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), "white")
    draw = ImageDraw.Draw(sheet)

    for item, pieces in items_data.items():
        for p in range(1, pieces + 1):
            if label_count >= MAX_LABELS:
                buf = io.BytesIO()
                sheet.save(buf, format="PNG", dpi=(DPI, DPI))
                sheets.append(buf.getvalue())
                sheet = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), "white")
                draw = ImageDraw.Draw(sheet)
                label_count = 0
                sheet_number += 1

            col = label_count % COLS
            row = label_count // COLS
            x = start_x + col * (LABEL_WIDTH_PX + h_spacing)
            y = start_y + row * (LABEL_HEIGHT_PX + v_spacing)

            draw.rectangle([x, y, x + LABEL_WIDTH_PX - 1, y + LABEL_HEIGHT_PX - 1], outline="black", width=1)

            lines = [
                f" DATE: {date}",
                f" INVOICE: {invoice_no}",
                f" SUPPLIER: {supplier}",
                "",
                f" ITEM: {item} ; PIECE: {p}/{pieces}"
            ]

            padding = 6
            line_heights = [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
            total_text_height = sum(line_heights)
            remaining_space = LABEL_HEIGHT_PX - 2 * padding - total_text_height
            line_spacing = int(remaining_space // (len(lines) - 1)) if len(lines) > 1 else 0

            current_y = y + padding
            for i, line in enumerate(lines):
                draw.text((x + padding, current_y), line, fill="black", font=font)
                current_y += line_heights[i] + line_spacing

            label_count += 1

    buf = io.BytesIO()
    sheet.save(buf, format="PNG", dpi=(DPI, DPI))
    sheets.append(buf.getvalue())

    return sheets, font_size, sheet_number

# --------- Main App ---------
def main():
    st.set_page_config(page_title="Wilton Weaver Labels", page_icon="🧶", layout="centered")
    set_wilton_theme()

    st.markdown('<h1 class="sticker-header">Wilton Weaver</h1>', unsafe_allow_html=True)
    st.markdown('<div class="company-subheader">Fine Carpet Label Generator • Est. 1984</div>', unsafe_allow_html=True)
    st.markdown("---")

    with st.container():
        st.markdown('<div class="sticker-form">', unsafe_allow_html=True)
        with st.form("label_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.text_input("📅 Date (e.g., 01-07-2024)")
                invoice_no = st.text_input("📄 Invoice Number (e.g., INV-123)")
            with col2:
                supplier = st.text_input("🏢 Supplier Name")
                num_items = st.number_input("📦 Number of Items", min_value=1, value=1)

            items_data = {}
            st.markdown("### 🧾 Item Details")
            for i in range(1, num_items + 1):
                pieces = st.number_input(f"Pieces for Item {i}", min_value=1, value=1, key=f"item_{i}")
                items_data[i] = pieces

            submitted = st.form_submit_button("✨ Generate Labels")
        st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        if not date or not invoice_no or not supplier:
            st.error("Please fill all fields!")
        else:
            with st.spinner("Generating labels..."):
                sheets, font_size, total_sheets = generate_invoice_labels(date, invoice_no, supplier, items_data)

            st.success(f"✅ {sum(items_data.values())} labels generated across {total_sheets} sheet(s)!")
            st.balloons()
            st.markdown("---")

            for idx, sheet_data in enumerate(sheets):
                st.markdown(f"### 📄 Sheet {idx + 1}")
                st.image(sheet_data, use_column_width=True)
                st.download_button(
                    label=f"⬇️ Download Sheet {idx + 1}",
                    data=sheet_data,
                    file_name=f"Wilton_Weaver_Sheet_{idx + 1}.png",
                    mime="image/png",
                    key=f"download_{idx}"
                )

if __name__ == "__main__":
    main()
