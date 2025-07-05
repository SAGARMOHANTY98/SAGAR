import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Custom CSS for sticker theme
def set_sticker_theme():
    st.markdown("""
    <style>
        /* Main container styling with sticker background */
        .stApp {
            background-image: url('https://img.freepik.com/free-vector/hand-drawn-sticker-collection_23-2149651206.jpg');
            background-size: cover;
            background-attachment: fixed;
            opacity: 0.9;
        }
        
        /* Form container with sticker-like appearance */
        .sticker-form {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 2px dashed #4CAF50;
            margin-bottom: 2rem;
        }
        
        /* Header styling */
        .sticker-header {
            color: #4CAF50;
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 1.5rem;
            font-weight: bold;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        }
        
        /* Input field styling */
        .stTextInput>div>div>input, .stTextArea>div>textarea {
            border-radius: 8px !important;
            border: 1px solid #4CAF50 !important;
        }
        
        /* Button styling */
        .stButton>button {
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton>button:hover {
            background-color: #45a049 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        }
        
        /* Success message */
        .stAlert {
            border-radius: 10px !important;
        }
        
        /* Download buttons */
        .stDownloadButton>button {
            background-color: #2196F3 !important;
        }
        
        /* Label preview */
        .stImage>img {
            border: 2px solid #4CAF50 !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Load font
def get_font(size):
    font_path = "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf"
    return ImageFont.truetype(font_path, size)

# Calculate optimal font size for a label
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

# Main label generation function
def generate_invoice_labels(date, invoice_no, supplier, items_data):
    DPI = 300
    A4_WIDTH_MM, A4_HEIGHT_MM = 210, 297
    A4_WIDTH_PX = int(A4_WIDTH_MM / 25.4 * DPI)
    A4_HEIGHT_PX = int(A4_HEIGHT_MM / 25.4 * DPI)
    LABEL_WIDTH_MM, LABEL_HEIGHT_MM = 37.02, 20.99
    LABEL_WIDTH_PX = int(LABEL_WIDTH_MM / 25.4 * DPI)
    LABEL_HEIGHT_PX = int(LABEL_HEIGHT_MM / 25.4 * DPI)
    COLS, ROWS = 5, 13
    MAX_LABELS_PER_SHEET = COLS * ROWS

    # Margins and spacing (mm to px)
    MARGIN_LEFT_RIGHT_MM = 6
    MARGIN_TOP_BOTTOM_MM = 12
    V_SPACING_MM, H_SPACING_MM = 0, 2
    MARGIN_LEFT_RIGHT_PX = int(MARGIN_LEFT_RIGHT_MM / 25.4 * DPI)
    MARGIN_TOP_BOTTOM_PX = int(MARGIN_TOP_BOTTOM_MM / 25.4 * DPI)
    v_spacing = int(V_SPACING_MM / 25.4 * DPI)
    h_spacing = int(H_SPACING_MM / 25.4 * DPI)

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

    sheet_number = 1
    label_count = 0
    sheets = []
    sheet = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), "white")
    draw = ImageDraw.Draw(sheet)

    for item_num, num_pieces in items_data.items():
        for piece_num in range(1, num_pieces + 1):
            if label_count >= MAX_LABELS_PER_SHEET:
                buf = io.BytesIO()
                sheet.save(buf, format="PNG", dpi=(DPI, DPI))
                sheets.append(buf.getvalue())
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
                outline="black", width=1
            )

            text_lines = [
                f" DATE: {date}",
                f" INVOICE: {invoice_no}",
                f" SUPPLIER: {supplier}",
                "",
                f" ITEM: {item_num} ; PIECE: {piece_num}/{num_pieces}"
            ]

            padding = 6
            line_heights = []
            for line in text_lines:
                bbox = font.getbbox(line)
                line_heights.append(bbox[3] - bbox[1])

            total_text_height = sum(line_heights)
            available_label_height = LABEL_HEIGHT_PX - 2 * padding
            remaining_space = available_label_height - total_text_height
            line_spacing = int(remaining_space // (len(text_lines) - 1)) * 0.76 if len(text_lines) > 1 else 0

            current_y = y + padding
            for i, line in enumerate(text_lines):
                draw.text((x + padding, current_y), line, fill="black", font=font)
                current_y += line_heights[i] + line_spacing

            label_count += 1

    # Save final sheet
    buf = io.BytesIO()
    sheet.save(buf, format="PNG", dpi=(DPI, DPI))
    sheets.append(buf.getvalue())

    return sheets, font_size, sheet_number

def main():
    # Set page config
    st.set_page_config(
        page_title="✨ Invoice Label Generator",
        page_icon="🏷️",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Set custom theme
    set_sticker_theme()
    
    # App header
    st.markdown('<h1 class="sticker-header">🏷️ Invoice Label Generator</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Main form in a sticker container
    with st.container():
        st.markdown('<div class="sticker-form">', unsafe_allow_html=True)
        
        with st.form("label_form"):
            # Form columns for better layout
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.text_input("📅 Date (e.g., 01-07-2024)")
                invoice_no = st.text_input("📄 Invoice Number (e.g., INV-123)")
            
            with col2:
                supplier = st.text_input("🏢 Supplier Name")
                num_items = st.number_input("📦 Number of Items", min_value=1, value=1, step=1)
            
            # Dynamic item input
            items_data = {}
            st.markdown("### 🧾 Item Details")
            for i in range(1, num_items + 1):
                pieces = st.number_input(
                    f"#️⃣ Pieces for Item {i}", 
                    min_value=1, 
                    value=1, 
                    step=1, 
                    key=f"item_{i}"
                )
                items_data[i] = pieces
            
            # Generate button with icon
            submitted = st.form_submit_button("✨ Generate Labels")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle form submission
    if submitted:
        if not date or not invoice_no or not supplier:
            st.error("Please fill in all required fields!")
        else:
            with st.spinner("🔄 Generating your labels..."):
                sheets, font_size, total_sheets = generate_invoice_labels(date, invoice_no, supplier, items_data)
            
            # Success message
            st.success(f"✅ Successfully generated {sum(items_data.values())} labels across {total_sheets} sheet(s)!")
            st.balloons()
            
            # Results section
            st.markdown("---")
            st.markdown("## 📋 Results")
            
            # Preview section
            with st.expander("🔍 Preview Settings", expanded=True):
                preview_col1, preview_col2 = st.columns(2)
                with preview_col1:
                    st.metric("Font Size Used", f"{font_size}pt")
                with preview_col2:
                    st.metric("Total Labels", sum(items_data.values()))
            
            # Display and download sheets
            for idx, sheet_data in enumerate(sheets):
                with st.container():
                    st.markdown(f"### 📄 Sheet {idx+1}")
                    
                    # Display the sheet
                    st.image(sheet_data, use_column_width=True)
                    
                    # Download button
                    st.download_button(
                        label=f"⬇️ Download Sheet {idx+1}",
                        data=sheet_data,
                        file_name=f"Invoice_Labels_Sheet_{idx+1}.png",
                        mime="image/png",
                        key=f"download_{idx}"
                    )
                
                st.markdown("---")

if __name__ == "__main__":
    main()
