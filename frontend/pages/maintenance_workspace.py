import streamlit as st
from components.style_loader import load_css
from api_client import upload_manual
from utils.shared_upload import get_shared_file, set_shared_file, clear_shared_file, SharedFileWrapper


def render():
    st.markdown('<div class="maintenance-page-title">🛠️ Maintenance Workspace</div>', unsafe_allow_html=True)

    load_css("maintenance_workspace.css")

    with st.container(border=True):
        st.markdown(
            """
            <div class="workspace-step-header">
                <span class="step-number">1</span>
                <div>
                    <div class="step-title">Upload Manual</div>
                    <div class="step-subtitle">Upload equipment manuals to improve AI-powered maintenance guidance.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        shared = get_shared_file()
        if shared:
            st.markdown(
                f"""
                <div class="file-chip">
                    📄 <b>{shared['name']}</b> (from Manual Library)
                    <span class="file-size">{shared['size'] / 1024:.1f} KB</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col_use, col_clear = st.columns(2)
            with col_use:
                use_shared = st.button("⬆ Upload this file", key="ws_use_shared", type="primary", use_container_width=True)
            with col_clear:
                if st.button("Choose a different file instead", key="ws_clear_shared", use_container_width=True):
                    clear_shared_file()
                    st.rerun()

            if use_shared:
                _do_upload(SharedFileWrapper(shared["name"], shared["bytes"]))
            return 

        uploaded_file = st.file_uploader(
            "Upload PDF", type="pdf", label_visibility="collapsed", key="workspace_upload"
        )

        if uploaded_file is not None:
            set_shared_file(uploaded_file) 
            st.markdown(
                f"""
                <div class="file-chip">
                    📄 <b>{uploaded_file.name}</b>
                    <span class="file-size">{uploaded_file.size / 1024:.1f} KB</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            upload_clicked = st.button("⬆ Upload Manual", key="workspace_upload_btn", type="primary")
            if upload_clicked:
                _do_upload(uploaded_file)


def _do_upload(file_obj):
    already_uploaded_key = "ws_last_uploaded_file"
    with st.spinner("Uploading, parsing, and embedding..."):
        try:
            result = upload_manual(file_obj)
            st.session_state[already_uploaded_key] = file_obj.name
            st.session_state["ws_upload_result"] = result
        except Exception as e:
            st.session_state[already_uploaded_key] = None
            st.session_state["ws_upload_result"] = None
            st.markdown(
                f'<div class="upload-result-box upload-error-box">❌ Upload failed: {e}</div>',
                unsafe_allow_html=True,
            )
            return

    result = st.session_state.get("ws_upload_result")
    if result:
        st.markdown(
            f"""
            <div class="upload-result-box upload-success-box">
                ✅ <b>{result['filename']}</b> indexed successfully —
                {result['pages_parsed']} pages, {result['chunks_created']} chunks.
            </div>
            """,
            unsafe_allow_html=True,
        )