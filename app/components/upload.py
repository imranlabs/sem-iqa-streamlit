import streamlit as st

ACCEPTED_TYPES = ["jpg", "jpeg", "png", "bmp", "tiff"]


def render_sidebar():
    """
    Renders the sidebar with image uploaders and run button.

    Returns
    -------
    ref_file  : UploadedFile or None
    test_file : UploadedFile or None
    run_clicked : bool
    """
    with st.sidebar:
        st.header("Images")

        ref_file = st.file_uploader(
            "Reference image",
            type=ACCEPTED_TYPES,
            help="Clean reference SEM image (e.g. post-PM Gold-on-Carbon)",
        )

        test_file = st.file_uploader(
            "Test image",
            type=ACCEPTED_TYPES,
            help="Test SEM image to evaluate against the reference",
        )

        st.divider()

        run_clicked = st.button(
            "Run Analysis",
            use_container_width=True,
            type="primary",
            disabled=(ref_file is None or test_file is None),
        )

    return ref_file, test_file, run_clicked
