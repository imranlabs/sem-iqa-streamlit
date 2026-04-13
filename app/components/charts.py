import streamlit as st
import numpy as np
import plotly.graph_objects as go


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
            
        x = list(range(256))
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x, y=hist_ref,
            mode="lines",
            name="Reference",
            line=dict(color="steelblue", width=1.5),
            fill="tozeroy",
            fillcolor="rgba(70,130,180,0.15)",
        ))
        fig.add_trace(go.Scatter(
            x=x, y=hist_test,
            mode="lines",
            name="Test",
            line=dict(color="tomato", width=1.5),
            fill="tozeroy",
            fillcolor="rgba(255,99,71,0.15)",
        ))
        fig.update_layout(
            xaxis=dict(title="Pixel intensity", range=[0, 255]),
            yaxis=dict(title="Normalised frequency"),
            height=350,
            margin=dict(l=20, r=20, t=20, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- Tool matching summary ---
    st.subheader("Tool matching summary")

    match_quality = histogram.get("match_quality", "N/A")
    colour_map = {"Excellent": "green", "Good": "green", "Fair": "orange", "Poor": "red"}
    st.markdown(
        f"**Match quality:** :{colour_map.get(match_quality, 'grey')}[{match_quality}]"
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Correlation",        f"{histogram.get('correlation_score') or 0:.3f}")
    col2.metric("Hellinger distance", f"{histogram.get('hellinger_distance') or 0:.3f}")
    col3.metric("Brightness Δ",       f"{histogram.get('brightness_difference') or 0:.1f}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Contrast ratio",     f"{histogram.get('contrast_ratio') or 0:.3f}")
    col5.metric("Dynamic range ref",  histogram.get("dynamic_range_ref") or 0)
    col6.metric("Dynamic range test", histogram.get("dynamic_range_test") or 0)


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
    col1.metric("Reference sharpness", f"{fft.get('fft_ref') or 0:.1f}")
    col2.metric("Test sharpness",      f"{fft.get('fft_test') or 0:.1f}")
    col3.metric("Sharpness ratio",     f"{fft.get('fft_ratio') or 0:.3f}")

    st.divider()

    # --- Interpretation guide ---
    with st.expander("How to interpret FFT spectra", expanded=False):
        st.markdown("""
        The FFT (Fast Fourier Transform) magnitude spectrum decomposes an image 
        into its spatial frequency components.

        **Center of the image** — low frequencies representing overall brightness 
        and large-scale structures. Always bright.

        **Edges and periphery** — high frequencies representing fine detail, 
        sharp edges, and texture. A sharp image has energy spread toward the edges.

        **What to look for:**
        - A sharp, well-focused image shows energy distributed across the full spectrum
        - A blurry or defocused image has energy concentrated near the center
        - The difference panel highlights where the two images diverge in frequency 
          content — warm colors (red) indicate the test has more energy at that 
          frequency, cool colors (blue) indicate less

        **Sharpness ratio** — test sharpness divided by reference sharpness. 
        Closer to 1.0 means the test image preserves the same frequency content 
        as the reference.
        """)

    st.divider()

    # --- FFT magnitude plots ---
    st.subheader("Magnitude spectra")

    ref_mag  = np.array(fft.get("ref_magnitude",  []))
    test_mag = np.array(fft.get("test_magnitude", []))
    diff_mag = np.array(fft.get("diff_magnitude", []))

    if ref_mag.size and test_mag.size and diff_mag.size:
        col1, col2, col3 = st.columns(3)

        with col1:
            fig = go.Figure(go.Heatmap(
                z=ref_mag,
                colorscale="Hot",
                colorbar=dict(title="log mag", thickness=12),
                showscale=True,
            ))
            fig.update_layout(
                title=dict(text=f"Reference — sharpness: {fft.get('fft_ref', 0):.1f}", font=dict(size=12)),
                height=300,
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(showticklabels=False),
                yaxis=dict(showticklabels=False, autorange="reversed"),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = go.Figure(go.Heatmap(
                z=test_mag,
                colorscale="Hot",
                colorbar=dict(title="log mag", thickness=12),
                showscale=True,
            ))
            fig.update_layout(
                title=dict(text=f"Test — sharpness: {fft.get('fft_test', 0):.1f}", font=dict(size=12)),
                height=300,
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(showticklabels=False),
                yaxis=dict(showticklabels=False, autorange="reversed"),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col3:
            fig = go.Figure(go.Heatmap(
                z=diff_mag,
                colorscale="RdBu_r",
                colorbar=dict(title="Δ log mag", thickness=12),
                showscale=True,
            ))
            fig.update_layout(
                title=dict(text=f"Difference (Test − Ref) — ratio: {fft.get('fft_ratio', 0):.3f}", font=dict(size=12)),
                height=300,
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(showticklabels=False),
                yaxis=dict(showticklabels=False, autorange="reversed"),
            )
            st.plotly_chart(fig, use_container_width=True)
    else: 
        st.warning("FFT magnitude data unavailable for this image pair.")
