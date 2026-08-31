import os
import sys
import time
from pathlib import Path
import streamlit as st

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Universal AI Tender & Proposal Analyzer",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
    .success-card {
        padding: 1.2rem;
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 8px;
        color: #166534;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📑 Universal AI Tender & Proposal Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">24-Point Executive Tender Discovery, Commercial BOQ Calculation & PDF Report Generator</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/color/96/analytical-skills.png", width=70)
    st.header("⚙️ Configuration")
    
    has_env_key = bool(os.environ.get("GEMINI_API_KEY"))
    api_key_input = st.text_input("Gemini API Key (Optional)", value="", type="password", placeholder="Paste key to override...", help="Leave blank to use key configured on server")
    
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
        st.success("✅ Custom Gemini API Key Applied")
    elif has_env_key:
        st.success("✅ API Key loaded securely from Environment")
    else:
        st.warning("⚠️ No Gemini API Key found. Paste key above or configure server secrets.")
        
    st.divider()
    st.markdown("### 📊 Features")
    st.markdown("- **4-Layer Discovery Engine**")
    st.markdown("- **Dynamic Table Extraction**")
    st.markdown("- **Commercial Cost Guard**")
    st.markdown("- **Executive PDF Generation**")

# Main Layout: File Uploaders
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Tender / RFP PDF(s)")
    uploaded_pdfs = st.file_uploader("Choose one or multiple PDF files for a single tender", type=["pdf"], accept_multiple_files=True, key="pdf_uploader")

with col2:
    st.subheader("2. Upload BOQ Excel (Optional)")
    uploaded_excel = st.file_uploader("Choose an Excel file (.xlsx / .xls)", type=["xlsx", "xls"], key="excel_uploader")

st.divider()

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

if uploaded_pdfs:
    for up_pdf in uploaded_pdfs:
        st.info(f"📄 Selected Tender PDF: **{up_pdf.name}** ({round(up_pdf.size / 1024 / 1024, 2)} MB)")
    if uploaded_excel:
        st.info(f"📊 Selected BOQ Excel: **{uploaded_excel.name}**")
        
    if st.button("🚀 Run AI Tender Analysis"):
        pdf_paths = []
        for up_pdf in uploaded_pdfs:
            p_path = INPUT_DIR / up_pdf.name
            with open(p_path, "wb") as f:
                f.write(up_pdf.getbuffer())
            pdf_paths.append(p_path)
            
        excel_path = None
        if uploaded_excel:
            excel_path = INPUT_DIR / uploaded_excel.name
            with open(excel_path, "wb") as f:
                f.write(uploaded_excel.getbuffer())

        st.subheader("🔄 Processing Pipeline")
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("1/4 Loading PDF(s) & Initializing 4-Layer Zero-Token Discovery Engine...")
        progress_bar.progress(25)

        # Import analyzer dynamically
        from tender_analyzer import process_pair, OUTPUT_DIR

        try:
            status_text.text("2/4 Executing Multi-Pass AI Extraction (Gemini API)...")
            progress_bar.progress(50)
            
            # Run processing engine
            process_pair(pdf_paths, excel_path)

            progress_bar.progress(85)
            status_text.text("3/4 Building Executive PDF Summary Report with ReportLab...")
            
            primary_stem = pdf_paths[0].stem
            output_pdf_path = OUTPUT_DIR / f"{primary_stem}_summary.pdf"

            if output_pdf_path.exists():
                progress_bar.progress(100)
                status_text.text("4/4 Done!")
                st.balloons()

                st.markdown(f'<div class="success-card">✅ <b>Tender Analysis Completed Successfully!</b><br>Executive report generated: <code>{output_pdf_path.name}</code></div>', unsafe_allow_html=True)

                with open(output_pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                    
                st.download_button(
                    label="📥 Download Executive Summary PDF Report",
                    data=pdf_bytes,
                    file_name=output_pdf_path.name,
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.error("❌ Could not find output PDF. Please check server logs.")
                
        except Exception as e:
            st.error(f"❌ An error occurred during analysis: {e}")
            st.exception(e)
else:
    st.info("💡 Please upload a Tender PDF above to get started.")
