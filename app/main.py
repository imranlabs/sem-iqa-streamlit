import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from app.core.config import settings

# Warm up the backend silently on app load
try:
    requests.get(f"{settings.backend_url}/ping", timeout=10)
except Exception:
    pass

import streamlit as st
from app.components.upload import render_sidebar
from app.components.metrics import render_metrics_tab
from app.components.charts import render_histogram_tab, render_fft_tab
from app.utils.api_client import fetch_analysis, fetch_fft


st.set_page_config(
    page_title="SEM IQA",
    page_icon="🔬",
    layout="wide",
)

st.title("SEM Image Quality Assessment")
st.caption("Tool-to-tool matching and image quality analysis for CD-SEM workflows.")
with st.expander("About this app", expanded=False):
        st.markdown("""
        **SEM Image Quality Assessment (IQA)** is a tool for quantifying and comparing 
        image quality between a reference and a test image.

        Originally designed for **CD-SEM metrology workflows** in semiconductor manufacturing, 
        the metrics are general-purpose and work on any image pair.

        **What it does:**
        - Computes full-reference metrics (SSIM, PSNR, Normalized Variance focus score)
        - Measures sharpness via Laplacian variance and FFT high-frequency energy
        - Compares pixel intensity distributions for tool-to-tool matching
        - Exports results as a timestamped CSV report

        **Image handling:**
        - All images are converted to grayscale internally regardless of input format
        - Accepted formats: JPG, PNG, BMP, TIFF
        - Maximum file size: 50MB per image
        - If reference and test images have different dimensions, both are resized 
        to the smaller of the two to avoid upsampling artifacts

        **Note on BRISQUE:**
                    
        BRISQUE is a no-reference perceptual quality metric included for completeness. 
        It is generally unreliable for SEM images due to their non-natural image statistics, 
        but may be informative for natural scene images.
                    
        ---
        **License:** MIT — free to use, modify, and distribute with attribution.  
        **Author:** Imran Khan · imransmailbox@gmail.com · [khanimran.com](https://khanimran.com)  
        © 2026 Imran Khan
        """)


# --- Sidebar ---
ref_file, test_file, run_clicked = render_sidebar()

# --- Main area ---

if run_clicked and ref_file and test_file:
    if ref_file.name == test_file.name and ref_file.size == test_file.size:
        st.info(
            "ℹ️ Reference and test appear to be the same file. "
            "Proceeding — expect SSIM = 1.0 and all ratios = 1.0."
        )
    with st.spinner("Running analysis..."):
        analysis = fetch_analysis(ref_file, test_file)
        fft = fetch_fft(ref_file, test_file)
    
    if analysis is None or fft is None:
        st.error("Analysis failed. Check that the backend is running.")
    else:
        if not analysis.get("shapes_matched"):
            ref_h, ref_w = analysis["ref_shape"]
            tst_h, tst_w = analysis["test_shape"]
            st.warning(
                f"⚠️ Images have different dimensions — "
                f"reference: {ref_w}×{ref_h}, test: {tst_w}×{tst_h}. "
                f"Both resized to {min(ref_w, tst_w)}×{min(ref_h, tst_h)} for comparison."
            )
        tab1, tab2, tab3 = st.tabs(["Metrics", "Histogram", "FFT"])
        with tab1:
            render_metrics_tab(ref_file, test_file, analysis, fft)
        with tab2:
            render_histogram_tab(ref_file, test_file, analysis)
        with tab3:
            render_fft_tab(fft)
else:
    st.info("Upload a reference and test image in the sidebar, then click **Run Analysis**.")


