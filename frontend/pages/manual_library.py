import streamlit as st
from components.style_loader import load_css
from api_client import (
    upload_manual,
    get_manuals,
    delete_manual,
    bulk_delete_manuals,
    get_view_url,
    get_download_url,
    download_manual_bytes,
)
from utils.shared_upload import set_shared_file, SharedFileWrapper


def _toggle_select_all():
    """Runs BEFORE the script reruns, so it's safe to set each checkbox's
    own session_state key here (this is the pattern Streamlit expects for
    syncing a 'select all' control with individually-keyed checkboxes)."""
    value = st.session_state.get("select_all_manuals", False)
    for name in st.session_state.get("_all_manual_names", []):
        st.session_state[f"chk_{name}"] = value


def render():
    st.markdown('<div class="library-page-title">📂 Manual Library</div>', unsafe_allow_html=True)

    load_css("manual_library.css")

    # ---------------- Upload New Manual ----------------
    with st.container(border=True):
        st.markdown('<div class="section-title">Upload New Manual</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed", key="library_uploader")

        if uploaded_file is not None:
            set_shared_file(uploaded_file)

            st.write(f"Selected: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

            col_upload, col_workspace = st.columns(2)
            with col_upload:
                if st.button("Upload & Ingest", type="primary", use_container_width=True):
                    with st.spinner("Parsing, chunking, and embedding..."):
                        try:
                            result = upload_manual(uploaded_file)
                            st.success(
                                f"✅ Ingested **{result['filename']}** — "
                                f"{result['pages_parsed']} pages, {result['chunks_created']} chunks."
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Upload failed: {e}")

            with col_workspace:
                if st.button("🛠 Use in Maintenance Workspace", use_container_width=True):
                    st.session_state.selected_page = "Maintenance Workspace"
                    st.query_params["page"] = "Maintenance Workspace"
                    st.rerun()

    # ---------------- Indexed Manuals ----------------
    with st.container(border=True):
        try:
            manuals = get_manuals()
        except Exception as e:
            st.error(f"Could not load manuals: {e}")
            manuals = []

        col_title, col_count = st.columns([3, 1])
        with col_title:
            st.markdown('<div class="section-title">Indexed Manuals</div>', unsafe_allow_html=True)
        with col_count:
            st.markdown(
                f'<div class="library-count" style="text-align:right;">{len(manuals)} manual(s) indexed</div>',
                unsafe_allow_html=True,
            )

        search = st.text_input("Search manuals", placeholder="Filter by name...", label_visibility="collapsed")
        if search:
            manuals = [m for m in manuals if search.lower() in m["name"].lower()]

        if not manuals:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="empty-state-icon">📂</div>
                    <div>No manuals indexed yet.</div>
                    <div style="font-size:0.8rem; margin-top:0.3rem;">
                        Upload a PDF above to get started.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        # Keep the current manual name list available to the select-all callback.
        st.session_state["_all_manual_names"] = [m["name"] for m in manuals]

        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.checkbox("Select all", key="select_all_manuals", on_change=_toggle_select_all)

        # Single source of truth: derive selection from each checkbox's own state,
        # instead of maintaining a separate set that can drift out of sync.
        selected_names = {name for name in st.session_state["_all_manual_names"] if st.session_state.get(f"chk_{name}", False)}

        with col_b:
            if selected_names:
                if st.button(f"🗑 Delete Selected ({len(selected_names)})", use_container_width=True):
                    st.session_state.confirm_bulk_delete = True

        if st.session_state.get("confirm_bulk_delete"):
            st.warning(f"Delete {len(selected_names)} selected manual(s)? This cannot be undone.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Yes, delete selected", type="primary"):
                    bulk_delete_manuals(list(selected_names))
                    for name in selected_names:
                        st.session_state[f"chk_{name}"] = False
                    st.session_state["select_all_manuals"] = False
                    st.session_state.confirm_bulk_delete = False
                    st.rerun()
            with c2:
                if st.button("Cancel"):
                    st.session_state.confirm_bulk_delete = False
                    st.rerun()

        st.markdown("<hr style='border-color:#2a3f5a;'>", unsafe_allow_html=True)

        for manual in manuals:
            name = manual["name"]

            with st.container(border=True, key=f"manual_card_{name}"):
                col_check, col_info, col_actions = st.columns([0.4, 4, 3])

                with col_check:
                    checked = st.checkbox(
                        "select",
                        value=st.session_state.get(f"chk_{name}", False),
                        key=f"chk_{name}",
                        label_visibility="collapsed",
                    )

                with col_info:
                    size_str = f"{manual['file_size_kb']} KB" if manual.get("file_size_kb") else "—"
                    date_str = manual.get("uploaded_at") or "—"

                    # Clicking the manual's name loads its PDF and jumps to
                    # the Maintenance Workspace, same as "Use in Workspace".
                    name_clicked = False
                    if manual.get("has_file"):
                        with st.container(key=f"name_wrap_{name}"):
                            name_clicked = st.button(
                                f"📄 {name}",
                                key=f"open_{name}",
                                type="tertiary",
                                help="Open this manual in the Maintenance Workspace",
                            )
                    else:
                        st.markdown(f"<span class='manual-name'>📄 {name}</span>", unsafe_allow_html=True)

                    st.markdown(
                        f"""
                        <div class="manual-meta">
                            {manual['pages']} pages · {manual['chunks']} chunks · {size_str} · Uploaded {date_str}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if name_clicked:
                        try:
                            with st.spinner(f"Loading {name}..."):
                                pdf_bytes = download_manual_bytes(name)
                            set_shared_file(SharedFileWrapper(name, pdf_bytes))
                            st.session_state.selected_page = "Maintenance Workspace"
                            st.query_params["page"] = "Maintenance Workspace"
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not load {name}: {e}")

                with col_actions:
                    b1, b2, b3 = st.columns(3)

                    with b1:
                        with st.container(key=f"view_wrap_{name}"):
                            if manual.get("has_file"):
                                st.link_button("👁", get_view_url(name), use_container_width=True)
                            else:
                                st.button("👁", disabled=True, use_container_width=True, key=f"view_{name}")

                    with b2:
                        with st.container(key=f"download_wrap_{name}"):
                            if manual.get("has_file"):
                                st.link_button("⬇️", get_download_url(name), use_container_width=True)
                            else:
                                st.button("⬇️", disabled=True, use_container_width=True, key=f"dl_{name}")

                    with b3:
                        with st.container(key=f"delete_wrap_{name}"):
                            if st.button("🗑", key=f"del_{name}", use_container_width=True):
                                st.session_state[f"confirm_delete_{name}"] = True

                if st.session_state.get(f"confirm_delete_{name}"):
                    st.warning(
                        f"Are you sure you want to delete **{name}**? "
                        "This action cannot be undone."
                    )

                    c1, c2 = st.columns(2)

                    with c1:
                        if st.button("Delete Manual", key=f"yes_{name}", type="primary"):
                            delete_manual(name)
                            st.session_state[f"confirm_delete_{name}"] = False
                            st.rerun()

                    with c2:
                        if st.button("Cancel", key=f"no_{name}"):
                            st.session_state[f"confirm_delete_{name}"] = False
                            st.rerun()