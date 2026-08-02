import streamlit as st
from components.style_loader import load_css
from api_client import upload_manual, get_manuals, delete_manual, bulk_delete_manuals, get_view_url, get_download_url

def render():
    load_css("manual_library.css")

    # ---------------- Upload New Manual ----------------
    with st.container(border=True):
        st.markdown('<div class="section-title">Upload New Manual</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")

        if uploaded_file is not None:
            st.write(f"Selected: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
            if st.button("Upload & Ingest", type="primary"):
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

        if "selected_manuals" not in st.session_state:
            st.session_state.selected_manuals = set()

        col_a, col_b = st.columns([3, 1])
        with col_a:
            select_all = st.checkbox("Select all")
            if select_all:
                st.session_state.selected_manuals = {m["name"] for m in manuals}
            elif not select_all and len(st.session_state.selected_manuals) == len(manuals):
                st.session_state.selected_manuals = set()

        with col_b:
            if st.session_state.selected_manuals:
                if st.button(f"🗑 Delete Selected ({len(st.session_state.selected_manuals)})", use_container_width=True):
                    st.session_state.confirm_bulk_delete = True

        if st.session_state.get("confirm_bulk_delete"):
            st.warning(f"Delete {len(st.session_state.selected_manuals)} selected manual(s)? This cannot be undone.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Yes, delete selected", type="primary"):
                    bulk_delete_manuals(list(st.session_state.selected_manuals))
                    st.session_state.selected_manuals = set()
                    st.session_state.confirm_bulk_delete = False
                    st.rerun()
            with c2:
                if st.button("Cancel"):
                    st.session_state.confirm_bulk_delete = False
                    st.rerun()

        st.markdown("<hr style='border-color:#2a3f5a;'>", unsafe_allow_html=True)

        for manual in manuals:
            name = manual["name"]
            st.markdown('<div class="manual-card">', unsafe_allow_html=True)

            col_check, col_info, col_actions = st.columns([0.4, 4, 3])

            with col_check:
                checked = st.checkbox(
                    "select", value=name in st.session_state.selected_manuals,
                    key=f"chk_{name}", label_visibility="collapsed",
                )
                if checked:
                    st.session_state.selected_manuals.add(name)
                else:
                    st.session_state.selected_manuals.discard(name)

            with col_info:
                size_str = f"{manual['file_size_kb']} KB" if manual.get("file_size_kb") else "—"
                date_str = manual.get("uploaded_at") or "—"
                st.markdown(
                    f"""
                    📄 <span class="manual-name">{name}</span>
                    <span class="status-indexed">✅ Indexed</span>
                    <div class="manual-meta">
                        {manual['pages']} pages · {manual['chunks']} chunks · {size_str} · Uploaded {date_str}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_actions:
                b1, b2, b3 = st.columns(3)

                with b1:
                    with st.container(key=f"view_wrap_{name}"):
                        if manual.get("has_file"):
                            st.link_button("👁  View", get_view_url(name), use_container_width=True)
                        else:
                            st.button("👁  View", disabled=True, use_container_width=True, key=f"view_{name}")

                with b2:
                    with st.container(key=f"download_wrap_{name}"):
                        if manual.get("has_file"):
                            st.link_button("⬇  Download", get_download_url(name), use_container_width=True)
                        else:
                            st.button("⬇  Download", disabled=True, use_container_width=True, key=f"dl_{name}")

                with b3:
                    with st.container(key=f"delete_wrap_{name}"):
                        if st.button("🗑  Delete", key=f"del_{name}", use_container_width=True):
                            st.session_state[f"confirm_delete_{name}"] = True

            if st.session_state.get(f"confirm_delete_{name}"):
                st.warning(f"Delete **{name}**?")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Yes, delete", key=f"yes_{name}", type="primary"):
                        delete_manual(name)
                        st.session_state[f"confirm_delete_{name}"] = False
                        st.rerun()
                with c2:
                    if st.button("Cancel", key=f"no_{name}"):
                        st.session_state[f"confirm_delete_{name}"] = False
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)