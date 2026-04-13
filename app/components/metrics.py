import streamlit as st
import numpy as np
from app.utils.report import generate_csv_report
from datetime import datetime
import os
import plotly.graph_objects as go




def _quality_badge(value: float, thresholds: tuple) -> str:
    """Return Excellent / Good / Fair / Poor label based on thresholds."""
    good, fair = thresholds
    if value >= good:
        return "🟢 Excellent" if value >= good * 1.1 else "🟢 Good"
    if value >= fair:
        return "🟡 Fair"
    return "🔴 Poor"


def render_metrics_tab(ref_file, test_file, analysis: dict, fft: dict):
    """
    Renders the Metrics tab.

    Parameters
    ----------
    ref_file, test_file : UploadedFile
    analysis            : dict — response from /api/v1/analyze
    """
    metrics = analysis.get("metrics", {})

    # --- Image thumbnails ---
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Reference image")
        st.image(ref_file, use_container_width=True)
    with col2:
        st.caption("Test image")
        st.image(test_file, use_container_width=True)

    st.divider()

    # --- Metric cards ---
    st.subheader("Key scores")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("SSIM", f"{metrics.get('ssim', 0):.3f}", help="Structural Similarity (higher = better)")
    c2.metric("PSNR", f"{metrics.get('psnr', 0):.1f} dB", help="Peak Signal-to-Noise Ratio (higher = better)")
    c3.metric("NV ratio", f"{metrics.get('nv_ratio', 0):.3f}", help="Normalized Variance focus ratio (closer to 1 = better)")
    c4.metric("Laplacian ratio", f"{metrics.get('laplacian_ratio', 0):.3f}", help="Sharpness ratio (closer to 1 = better)")
    c5.metric("CNR ratio", f"{metrics.get('cnr_ratio', 0):.3f}", 
          help="Contrast-to-Noise Ratio (closer to 1 = better)")
    st.divider()

    # --- Score breakdown bar chart ---
    st.subheader("Score breakdown")
       
    labels = ["SSIM", "NV ratio", "Laplacian ratio", "FFT ratio", "CNR ratio"]
    keys   = ["ssim", "nv_ratio", "laplacian_ratio", "fft_ratio", "cnr_ratio"]
    values = [float(metrics.get(k) or 0) for k in keys]
    colours = [
        "#1D9E75" if v > 0.8 else "#BA7517" if v > 0.5 else "#A32D2D"
        for v in values
    ]

    fig = go.Figure()
    MIN_BAR = 0.02
    for label, val, colour in zip(labels, values, colours):
        fig.add_trace(go.Bar(
            x=[max(val, MIN_BAR)],
            y=[label],
            orientation="h",
            marker_color=colour,
            text=f"{val:.3f}",
            textposition="outside",
            showlegend=False,
        ))

    fig.add_vline(x=1.0, line_dash="dash", line_color="grey")
    fig.update_layout(
        xaxis=dict(range=[0, 1.2], title="Score (closer to 1 is better)"),
        yaxis=dict(autorange="reversed"),
        height=300,
        margin=dict(l=20, r=60, t=20, b=40),
        bargap=0.4,
    )

    st.plotly_chart(fig, use_container_width=True)
   

    st.divider()

    # --- Quality assessment table ---
    st.subheader("Quality assessment")
    ssim  = metrics.get("ssim", 0) or 0
    psnr  = metrics.get("psnr", 0) or 0
    nv    = metrics.get("nv_ratio", 0) or 0
    lap   = metrics.get("laplacian_ratio", 0) or 0
    cnr   = metrics.get("cnr_ratio", 0) or 0

    st.table({
        "Metric":        ["SSIM", "PSNR", "NV ratio", "Laplacian ratio", "CNR ratio"],
        "Value":         [f"{ssim:.3f}", f"{psnr:.1f} dB", f"{nv:.3f}", f"{lap:.3f}",f"{cnr:.3f}" ],
        "Rating":        [
            _quality_badge(ssim, (0.8, 0.6)),
            _quality_badge(psnr / 50, (0.8, 0.4)),   # normalise PSNR to 0-1
            _quality_badge(min(nv, 1.0), (0.8, 0.5)),
            _quality_badge(min(lap, 1.0), (0.8, 0.5)),
            _quality_badge(min(cnr, 1.0), (0.8, 0.5))
        ],
        "Ideal":         ["1.000", "∞ dB", "1.000", "1.000", "1.000"],
    })
    st.divider()

    with st.expander("BRISQUE score (experimental)"):
        st.caption(
            "BRISQUE is a no-reference perceptual quality metric. "
            "It is included for completeness but is generally not reliable "
            "for SEM images due to their non-natural image statistics."
        )
        brisque_ref  = metrics.get("brisque_ref")
        brisque_test = metrics.get("brisque_test")
        col1, col2 = st.columns(2)
        col1.metric(
            "BRISQUE reference",
            f"{brisque_ref:.1f}" if brisque_ref is not None else "N/A",
            help="Lower is better. Unreliable for SEM images.",
        )
        col2.metric(
            "BRISQUE test",
            f"{brisque_test:.1f}" if brisque_test is not None else "N/A",
            help="Lower is better. Unreliable for SEM images.",
        )

    st.divider()

    csv_bytes = generate_csv_report(
        ref_filename=ref_file.name,
        test_filename=test_file.name,
        analysis=analysis,
        fft=fft,
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    base_name = os.path.splitext(test_file.name)[0].replace(" ", "_")
    st.download_button(
        label="Download analysis report (CSV)",
        data=csv_bytes,
        file_name=f"{base_name}_iqa_{timestamp}.csv",
        mime="text/csv",
        use_container_width=True,
    )


