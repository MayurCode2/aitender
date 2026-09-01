import os
import sys
import time
from pathlib import Path
import streamlit as st

# Setup base input & output directory constants
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

def cleanup_old_files():
    """Removes all old uploaded and generated files/folders to keep storage clean."""
    cleaned_count = 0
    for base_dir in [INPUT_DIR, OUTPUT_DIR]:
        for item in base_dir.glob("*"):
            if item.is_file():
                try:
                    item.unlink()
                    cleaned_count += 1
                except Exception:
                    pass
            elif item.is_dir():
                try:
                    for child in item.glob("*"):
                        if child.is_file():
                            child.unlink()
                    item.rmdir()
                    cleaned_count += 1
                except Exception:
                    pass
    return cleaned_count

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
    api_key_input = st.text_input("Gemini API Key", value="", type="password", placeholder="Enter your Gemini API Key...", help="Leave blank if pre-configured on server")
    
    if api_key_input:
        st.success("✅ Custom Gemini API Key provided")
    elif has_env_key:
        st.success("✅ API Key loaded securely from Server Environment")
    else:
        st.warning("⚠️ No Gemini API Key found. Paste key above or configure server secrets.")
        
    st.divider()
    st.markdown("### 📊 Features")
    st.markdown("- **4-Layer Discovery Engine**")
    st.markdown("- **Dynamic Table Extraction**")
    st.markdown("- **Commercial Cost Guard**")
    st.markdown("- **Executive PDF Generation**")
    
    st.divider()
    st.markdown("### 🗑️ Storage Management")
    if st.button("🧹 Remove All Old Docs", help="Clears old input files and generated summaries"):
        num_removed = cleanup_old_files()
        st.sidebar.success(f"Cleaned {num_removed} old file(s)!")

# Main Layout: File Uploaders
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Tender / RFP PDF(s)")
    uploaded_pdfs = st.file_uploader("Choose one or multiple PDF files for a single tender", type=["pdf"], accept_multiple_files=True, key="pdf_uploader")

with col2:
    st.subheader("2. Upload BOQ Excel (Optional)")
    uploaded_excel = st.file_uploader("Choose an Excel file (.xlsx / .xls)", type=["xlsx", "xls"], key="excel_uploader")

st.divider()

# Auto-cleanup old files when uploaded document selection changes
current_pdf_names = set(up.name for up in uploaded_pdfs) if uploaded_pdfs else set()
current_excel_name = uploaded_excel.name if uploaded_excel else None
current_upload_signature = (tuple(sorted(current_pdf_names)), current_excel_name)

if "last_upload_signature" not in st.session_state:
    st.session_state.last_upload_signature = None

if st.session_state.last_upload_signature != current_upload_signature:
    cleaned = cleanup_old_files()
    st.session_state.last_upload_signature = current_upload_signature
    if cleaned > 0 and (uploaded_pdfs or uploaded_excel):
        st.toast(f"🧹 Removed {cleaned} old file(s) for fresh upload.", icon="✨")

if uploaded_pdfs:
    for up_pdf in uploaded_pdfs:
        st.info(f"📄 Selected Tender PDF: **{up_pdf.name}** ({round(up_pdf.size / 1024 / 1024, 2)} MB)")
    if uploaded_excel:
        st.info(f"📊 Selected BOQ Excel: **{uploaded_excel.name}**")
        
    if st.button("🚀 Run AI Tender Analysis"):
        active_key = api_key_input.strip() if api_key_input else None
        if not active_key and not os.environ.get("GEMINI_API_KEY"):
            st.error("❌ **Gemini API Key Missing!** Please paste your Gemini API key in the sidebar configuration to run the analysis.")
            st.stop()

        # Auto-clean previous files before saving new ones
        cleanup_old_files()

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
            status_text.text("2/4 Executing Multi-Pass AI Extraction (Google Gemini API)...")
            progress_bar.progress(50)
            
            # Run processing engine
            process_pair(pdf_paths, excel_path, api_key=active_key)

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
            progress_bar.progress(100)
            status_text.empty()
            st.error(f"❌ **Gemini API / Analysis Error:** {e}")
            st.warning("💡 **Troubleshooting Tips:**\n- Verify that your Gemini API Key entered in the sidebar is valid.\n- Check if your Google AI Studio quota / rate limit has been exceeded.\n- Ensure your network connection can access Google Gemini services.")
else:
    st.info("💡 Please upload a Tender PDF above to get started.")
