"""
Shared upload state — lets a file selected on one page (e.g. Manual
Library) be reused on another page (e.g. Maintenance Workspace) without
re-selecting it, since Streamlit's file_uploader widgets don't share
state across pages by default.
"""
import streamlit as st


def set_shared_file(uploaded_file):
    """Store the selected file's bytes/name so other pages can reuse it."""
    if uploaded_file is not None:
        st.session_state["shared_pdf_bytes"] = uploaded_file.getvalue()
        st.session_state["shared_pdf_name"] = uploaded_file.name
        st.session_state["shared_pdf_size"] = uploaded_file.size


def get_shared_file():
    """Return (name, size, bytes) of the currently shared file, or None."""
    name = st.session_state.get("shared_pdf_name")
    if not name:
        return None
    return {
        "name": name,
        "size": st.session_state.get("shared_pdf_size", 0),
        "bytes": st.session_state.get("shared_pdf_bytes"),
    }


def clear_shared_file():
    for key in ("shared_pdf_bytes", "shared_pdf_name", "shared_pdf_size"):
        st.session_state.pop(key, None)


class SharedFileWrapper:
    """
    Mimics Streamlit's UploadedFile interface (.name, .size, .getvalue())
    so the shared bytes can be passed directly into upload_manual() /
    set_shared_file() the same way a fresh file_uploader result would be.
    """
    def __init__(self, name: str, data: bytes, size: int = None):
        self.name = name
        self._data = data
        self.size = size if size is not None else len(data)

    def getvalue(self):
        return self._data