import os
import sys
import tempfile
import streamlit as st
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Ensure src/ is on the path so the package is always found
_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

try:
    from fact_checker.crew import FactChecker
    from fact_checker.tools import FileReaderTool
except ImportError as e:
    st.error(f"Could not import TruthLens modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="TruthLens — AI Fact Checking",
    layout="wide",
    page_icon="🔍",
    initial_sidebar_state="collapsed"
)

# Load CSS from external file (keeps Python clean, eliminates linter false positives)
_css_path = os.path.join(os.path.dirname(__file__), "styles.css")
with open(_css_path, "r", encoding="utf-8") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">TruthLens</h1>
    <p class="main-subtitle">AI-Powered Fact Verification System</p>
</div>
""", unsafe_allow_html=True)

# Environment check
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ **Configuration Error:** Please set your OPENAI_API_KEY in the .env file")
    st.stop()

# Features overview
st.markdown('<h2 class="section-header">🚀 Platform Capabilities</h2>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🗣️ Text Claims</div>
        <div class="feature-description">Advanced AI verification of factual statements, assertions, and textual content with comprehensive source validation</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🌐 Web Content</div>
        <div class="feature-description">Real-time analysis of articles, news content, and online publications with cross-referencing capabilities</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📺 Video Content</div>
        <div class="feature-description">Intelligent fact-checking of YouTube videos, transcripts, and multimedia content claims</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📄 Documents</div>
        <div class="feature-description">Comprehensive processing and verification of PDF documents, Word files, and text-based materials</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Input section
st.markdown("""
<div class="input-section">
""", unsafe_allow_html=True)

st.markdown('<h3 class="section-header">🎯 Select Verification Method</h3>', unsafe_allow_html=True)

# Input mode selection
mode = st.radio(
    "Select Mode",
    ["📝 Text Claim", "🌐 Website URL", "📺 YouTube Video", "📄 Document Upload"],
    horizontal=True,
    key="input_mode"
)

st.markdown("<br>", unsafe_allow_html=True)

user_input = ""
claim, url, youtube_url, uploaded_file = "", "", "", None

# Input forms based on selected mode
if mode == "📝 Text Claim":
    st.markdown("**Enter the factual claim you want to verify:**")
    claim = st.text_area(
        "Enter your claim",
        height=120,
        placeholder="Enter the statement or claim you want to fact-check...",
        key="claim_input"
    )
    user_input = claim

elif mode == "🌐 Website URL":
    st.markdown("**Enter the website URL to analyze:**")
    url = st.text_input(
        "",
        placeholder="https://example.com/article",
        key="url_input"
    )
    user_input = url

elif mode == "📺 YouTube Video":
    st.markdown("**Enter the YouTube video URL:**")
    youtube_url = st.text_input(
        "",
        placeholder="https://www.youtube.com/watch?v=...",
        key="youtube_input"
    )
    if youtube_url:
        if re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?#]+)', youtube_url):
            st.success("✅ Valid YouTube URL detected")
        else:
            st.warning("⚠️ Please enter a valid YouTube URL")
    user_input = youtube_url

elif mode == "📄 Document Upload":
    st.markdown("**Upload a document for analysis:**")
    uploaded_file = st.file_uploader(
        "",
        type=["pdf", "docx", "txt"],
        help="Supported formats: PDF, Word Document (.docx), Text File (.txt)"
    )
    if uploaded_file:
        st.success(f"✅ File uploaded: **{uploaded_file.name}** ({round(uploaded_file.size/1024, 1)} KB)")

st.markdown("</div>", unsafe_allow_html=True)

# Analysis button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button(
        "🚀 Launch Professional Analysis",
        use_container_width=True,
        key="analyze_btn"
    )

# Analysis execution
if analyze_button:
    # Input validation
    has_input = bool(claim or url or youtube_url or uploaded_file)
    
    if not has_input:
        st.error("⚠️ **Input Required:** Please provide content to analyze before starting the verification process.")
        st.stop()
    
    # Processing indicator
    with st.spinner("🔍 **TruthLens Analysis in Progress** — Our AI agents are researching, analyzing, and verifying your content..."):
        input_content = ""

        # File processing — delegated to FileReaderTool (single source of truth)
        if uploaded_file:
            suffix = os.path.splitext(uploaded_file.name)[1].lower()
            if suffix not in (".pdf", ".docx", ".txt"):
                st.error("❌ **Unsupported Format:** Please upload a PDF, Word document, or text file.")
                st.stop()
            try:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=suffix
                ) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                input_content = FileReaderTool()._run(tmp_path)
                os.unlink(tmp_path)  # clean up temp file
            except Exception as e:
                st.error(f"❌ **File Processing Error:** {e}")
                st.stop()
        else:
            input_content = claim or url or youtube_url

        # Run analysis
        try:
            progress = st.progress(0, text="Initializing TruthLens...")
            progress.progress(20, text="Loading AI agents...")
            checker = FactChecker()
            progress.progress(60, text="Executing multi-agent analysis...")
            result = checker.crew().kickoff(inputs={"input_content": input_content})
            progress.progress(100, text="Analysis complete!")
        except Exception as e:
            st.error(f"❌ **Analysis Error:** {e}")
            st.stop()

    # Success notification
    st.success("🎉 **Analysis Complete** - Professional verification report generated successfully")

    # Results section
    st.markdown("""
    <div class="results-section">
    """, unsafe_allow_html=True)

    # Verdict analysis and display
    result_text = str(result)
    result_lower = result_text.lower()

    st.markdown("### 📊 Verification Result")
    
    # Determine verdict
    if "true" in result_lower and "false" not in result_lower:
        st.markdown("""
        <div class="verdict-container verdict-true">
            ✅ VERDICT: THE PROVIDED INFORMATION IS TRUE
        </div>
        """, unsafe_allow_html=True)
    elif "false" in result_lower:
        st.markdown("""
        <div class="verdict-container verdict-false">
            ❌ VERDICT: THE PROVIDED INFORMATION IS FALSE
        </div>
        """, unsafe_allow_html=True)
    elif "misleading" in result_lower or "partially" in result_lower:
        st.markdown("""
        <div class="verdict-container verdict-partial">
            ⚠️ VERDICT: THE PROVIDED INFORMATION IS PARTIALLY ACCURATE
        </div>
        """, unsafe_allow_html=True)
    elif "INCONCLUSIVE" in result_lower:
        st.markdown("""
        <div class="verdict-container verdict-inconclusive">
            🔍 VERDICT: REQUIRES FURTHER INVESTIGATION
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="verdict-container verdict-inconclusive">
            📋 DETAILED ANALYSIS AVAILABLE
        </div>
        """, unsafe_allow_html=True)

    # Detailed report
    st.markdown("### 📄 Comprehensive Analysis Report")
    with st.expander("**Click to view detailed verification report**", expanded=True):
        st.markdown(result_text)

    st.markdown("</div>", unsafe_allow_html=True)

    # Download options
    st.markdown("### 📥 Export Options")
    col1, col2 = st.columns(2)

    with col1:
        # Text report
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as f:
            report_header = f"TRUTHLENS VERIFICATION REPORT\n{'='*50}\n\n"
            report_header += f"Input Content: {input_content[:200]}{'...' if len(input_content) > 200 else ''}\n\n"
            report_header += f"Analysis Results:\n{'-'*20}\n\n{result_text}"
            f.write(report_header)
            temp_path = f.name
        
        with open(temp_path, "rb") as f:
            st.download_button(
                "📄 Download as Text Report",
                f.read(),
                "truthlens_verification_report.txt",
                mime="text/plain",
                use_container_width=True
            )

    with col2:
        # Markdown report
        md_report = f"""# TruthLens Verification Report

## Input Analysis
**Content:** {input_content[:200]}{'...' if len(input_content) > 200 else ''}

## Verification Results

{result_text}

---
*Generated by TruthLens — AI-Powered Fact-Checking System*
*Built by Likhith Thallam | Powered by Multi-Agent Intelligence*
"""
        st.download_button(
            "📋 Download as Markdown",
            md_report,
            "truthlens_verification_report.md",
            mime="text/markdown",
            use_container_width=True
        )

# Simple Professional Footer - Fixed Copyright Display
# Simple Professional Footer - Fixed Copyright Display
st.markdown("""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    padding: 2rem;
    border-radius: 15px;
    margin-top: 3rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
">
    <p style="
        color: white !important;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    ">Built by Likhith Thallam</p>
    <p style="
        color: rgba(255,255,255,0.8) !important;
        font-size: 0.95rem;
        margin: 0;
    ">© 2026 TruthLens — All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
