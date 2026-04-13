# sem-iqa-frontend/app/utils/report.py
import io
import csv
from datetime import datetime




def generate_csv_report(
    ref_filename: str,
    test_filename: str,
    analysis: dict,
    fft: dict,
) -> bytes:
    """
    Generate a flat CSV report from analysis and FFT results.

    Returns
    -------
    bytes — UTF-8 encoded CSV content ready for st.download_button
    """
    metrics   = analysis.get("metrics", {})
    histogram = analysis.get("histogram", {})
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    rows = [
        # Header info
        ("timestamp",          timestamp),
        ("reference_file",     ref_filename),
        ("test_file",          test_filename),
        ("shapes_matched",     analysis.get("shapes_matched", "")),
        ("ref_shape",          "x".join(str(v) for v in analysis.get("ref_shape", []))),
        ("test_shape",         "x".join(str(v) for v in analysis.get("test_shape", []))),

        # Full-reference metrics
        ("ssim",               metrics.get("ssim", "")),
        ("psnr_db",            metrics.get("psnr", "")),
        ("nv_ref",             metrics.get("nv_ref", "")),
        ("nv_test",            metrics.get("nv_test", "")),
        ("nv_ratio",           metrics.get("nv_ratio", "")),
        ("laplacian_ref",      metrics.get("laplacian_ref", "")),
        ("laplacian_test",     metrics.get("laplacian_test", "")),
        ("laplacian_ratio",    metrics.get("laplacian_ratio", "")),
        ("cnr_ref",   metrics.get("cnr_ref", "")),
        ("cnr_test",  metrics.get("cnr_test", "")),
        ("cnr_ratio", metrics.get("cnr_ratio", "")),
        ("fft_ref",            fft.get("fft_ref", "")),
        ("fft_test",           fft.get("fft_test", "")),
        ("fft_ratio",          fft.get("fft_ratio", "")),
        ("fft_difference",     fft.get("fft_difference", "")),
        ("brisque_ref",        metrics.get("brisque_ref", "")),
        ("brisque_test",       metrics.get("brisque_test", "")),
       

        # Histogram / tool matching
        ("correlation_score",      histogram.get("correlation_score", "")),
        ("chi_square",             histogram.get("chi_square", "")),
        ("hellinger_distance",     histogram.get("hellinger_distance", "")),
        ("intersection",           histogram.get("intersection", "")),
        ("ref_brightness",         histogram.get("ref_brightness", "")),
        ("ref_contrast",           histogram.get("ref_contrast", "")),
        ("test_brightness",        histogram.get("test_brightness", "")),
        ("test_contrast",          histogram.get("test_contrast", "")),
        ("brightness_difference",  histogram.get("brightness_difference", "")),
        ("contrast_ratio",         histogram.get("contrast_ratio", "")),
        ("dynamic_range_ref",      histogram.get("dynamic_range_ref", "")),
        ("dynamic_range_test",     histogram.get("dynamic_range_test", "")),
        ("match_quality",          histogram.get("match_quality", "")),
    ]

   
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["metric", "value"])
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")
