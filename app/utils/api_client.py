import requests
import streamlit as st
from app.core.config import settings


def fetch_analysis(ref_file, test_file) -> dict | None:
    """
    POST reference and test images to /api/v1/analyze.

    Returns the parsed JSON response or None on failure.
    """
    try:
        ref_file.seek(0)
        test_file.seek(0)
        response = requests.post(
            f"{settings.backend_url}/api/v1/analyze",
            files={
                "reference": (ref_file.name, ref_file, ref_file.type),
                "test":      (test_file.name, test_file, test_file.type),
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the backend. Is it running?")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Backend error: {e.response.status_code} — {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def fetch_fft(ref_file, test_file) -> dict | None:
    """
    POST reference and test images to /api/v1/fft.

    Returns the parsed JSON response or None on failure.
    """
    try:
        ref_file.seek(0)
        test_file.seek(0)
        response = requests.post(
            f"{settings.backend_url}/api/v1/fft",
            files={
                "reference": (ref_file.name, ref_file, ref_file.type),
                "test":      (test_file.name, test_file, test_file.type),
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the backend. Is it running?")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Backend error: {e.response.status_code} — {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None
