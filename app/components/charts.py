import streamlit as st
import matplotlib.pyplot as plt
import numpy as np


def render_histogram_tab(ref_file, test_file, analysis: dict):
    """
    Renders the Histogram tab.

    Parameters
    ----------
    ref_file, test_file : UploadedFile
    analysis            : dict — response from /api/v1/analyze
    """
    histogram = analysis.get("histogram", {})

    # --- Image thumbnails ---
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"Reference — brightness: {histogram.get('ref_brightness', 0):.1f}")
        st.image(ref_file, use_container_width=True)
    with col2:
        st.caption(f"Test — brightness: {histogram.get('test_brightness', 0):.1f}")
        st.image(test_file, use_container_width=True)

    st.divider()

    # --- Overlapping histograms ---
    st.subheader("Histogram comparison")

    hist_ref  = histogram.get("hist_ref", [])
    hist_test = histogram.get("hist_test", [])

    if hist_ref and hist_test:
        fig, ax = plt.subplots(figsize=(9, 3.5))
        ax.plot(hist_ref,  color="steelblue", alpha=0.8, label="Reference")
        ax.plot(hist_test, color="tomato",    alpha=0.8, label="Test")
        ax.set_xlabel("Pixel intensity")
        ax.set_ylabel("Normalised frequency")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.divider()

    # --- Tool matching summary ---
    st.subheader("Tool matching summary")

    match_quality = histogram.get("match_quality", "N/A")
    colour_map = {"Excellent": "green", "Good": "green", "Fair": "orange", "Poor": "red"}
    st.markdown(
        f"**Match quality:** :{colour_map.get(match_quality, 'grey')}[{match_quality}]"
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Correlation",        f"{histogram.get('correlation_score', 0):.3f}")
    col2.metric("Hellinger distance", f"{histogram.get('hellinger_distance', 0):.3f}")
    col3.metric("Brightness Δ",       f"{histogram.get('brightness_difference', 0):.1f}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Contrast ratio",     f"{histogram.get('contrast_ratio', 0):.3f}")
    col5.metric("Dynamic range ref",  histogram.get("dynamic_range_ref", 0))
    col6.metric("Dynamic range test", histogram.get("dynamic_range_test", 0))


def render_fft_tab(fft: dict):
    """
    Renders the FFT tab.

    Parameters
    ----------
    fft : dict — response from /api/v1/fft
    """
    st.subheader("FFT spectrum analysis")

    # --- Score cards ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Reference sharpness", f"{fft.get('fft_ref', 0):.1f}")
    col2.metric("Test sharpness",      f"{fft.get('fft_test', 0):.1f}")
    col3.metric("Sharpness ratio",     f"{fft.get('fft_ratio', 0):.3f}")

    st.divider()

    # --- FFT magnitude plots ---
    st.subheader("Magnitude spectra")

    ref_mag  = np.array(fft.get("ref_magnitude",  []))
    test_mag = np.array(fft.get("test_magnitude", []))
    diff_mag = np.array(fft.get("diff_magnitude", []))

    if ref_mag.size and test_mag.size and diff_mag.size:
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14, 4))

        ax1.imshow(ref_mag,  cmap="hot")
        ax1.set_title(f"Reference\nSharpness: {fft.get('fft_ref', 0):.1f}")
        ax1.axis("off")

        ax2.imshow(test_mag, cmap="hot")
        ax2.set_title(f"Test\nSharpness: {fft.get('fft_test', 0):.1f}")
        ax2.axis("off")

        ax3.imshow(diff_mag, cmap="coolwarm")
        ax3.set_title(f"Difference (Test − Ref)\nRatio: {fft.get('fft_ratio', 0):.3f}")
        ax3.axis("off")

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
