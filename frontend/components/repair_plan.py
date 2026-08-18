"""
Step 3 of the Maintenance Dashboard — the AI Repair Plan section.

The backend's /iot-alert endpoint returns the repair plan as a single block of
free-text markdown written by the LLM, following the section order defined in
backend/app/prompts/repair_prompt.py (SECTION 0, 0B, 0C, then 1-6). This module
splits that text back into its sections and renders them as the result cards.

Kept self-contained on purpose: it only reads the /iot-alert response that is
handed to it, so Step 2 (the alert simulator) stays independent of it. Step 2
stores that response in session state, so the call from dashboard.py is:

    from components.repair_plan import render_repair_plan
    render_repair_plan(st.session_state.get("latest_repair_plan"))
"""
import html
import re

import streamlit as st

from api_client import get_view_url
from components.style_loader import load_css

# Section keys in the order the prompt asks the LLM to write them.
SECTION_KEYS = [
    "verification",
    "variants",
    "scope",
    "diagnosis",
    "procedure",
    "tools",
    "parts",
    "safety",
    "references",
]

# Numbered sections 1-6, with the keywords that confirm a line is really that
# heading and not just a numbered step inside the repair procedure.
_NUMBERED_SECTIONS = {
    "1": ("diagnosis", ("diagnos", "problem")),
    "2": ("procedure", ("repair", "procedure", "step")),
    "3": ("tools", ("tool",)),
    "4": ("parts", ("part", "spare")),
    "5": ("safety", ("safety", "precaution")),
    "6": ("references", ("manual", "reference")),
}

# Fallback for when the LLM drops the numbers and writes only the title.
_TITLE_ONLY_SECTIONS = [
    ("diagnosis", ("problem diagnosis",)),
    ("procedure", ("repair procedure", "step-by-step")),
    ("tools", ("required tools",)),
    ("parts", ("required spare parts", "spare parts")),
    ("safety", ("safety precautions",)),
    ("references", ("manual references",)),
]

_MAX_HEADING_LEN = 90
_LIST_ITEM = re.compile(r"^\s*(?:\d+[\.\)]|[-*•‣●▪])\s+(.*)$")
# Steps written inline on one line, e.g. "1) Stop the motor. 2) Regrease it."
_INLINE_STEP = re.compile(r"(?:^|\s)\d+[\.\)]\s+")
# Words that commonly precede a cited filename and must not become part of it.
_CITATION_LEAD_IN = re.compile(
    r"^(?:see|refer\s+to|refer|per|in|from|the|section|source|document)\s+", re.IGNORECASE
)


def _strip_markdown(line: str) -> str:
    """Reduce a line to its bare text so headings can be matched regardless of
    whether the LLM decorated them with #, ** or trailing colons."""
    cleaned = line.strip()
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned)
    cleaned = cleaned.replace("*", "").replace("_", "").replace("`", "")
    return cleaned.strip().strip(":").strip()


def _match_heading(line: str):
    """Return the section key this line starts, or None if it isn't a heading."""
    bare = _strip_markdown(line)
    if not bare or len(bare) > _MAX_HEADING_LEN:
        return None

    lowered = bare.lower()

    # SECTION 0C / 0B / 0 — longest suffix first so "0C" never matches as "0".
    section_zero = re.match(r"^section\s*0\s*([bc])?\b", lowered)
    if section_zero:
        suffix = section_zero.group(1)
        return {"c": "scope", "b": "variants", None: "verification"}[suffix]

    # "1. Problem Diagnosis", "SECTION 2 - ...", "### 5) Safety Precautions"
    numbered = re.match(r"^(?:section\s*)?([1-6])\s*[\.\)\:\-–—]?\s*(.*)$", lowered)
    if numbered:
        key, keywords = _NUMBERED_SECTIONS[numbered.group(1)]
        remainder = numbered.group(2)
        if any(word in remainder for word in keywords):
            return key

    for key, phrases in _TITLE_ONLY_SECTIONS:
        if any(lowered.startswith(phrase) for phrase in phrases):
            return key

    return None


def parse_repair_plan(plan_text: str) -> dict:
    """Split the LLM's free-text plan into its named sections.

    Any text before the first recognised heading is kept under "preamble" so
    nothing the model wrote is silently dropped. Sections the model omitted come
    back as empty strings rather than missing keys.
    """
    sections = {key: "" for key in SECTION_KEYS}
    sections["preamble"] = ""

    if not plan_text or not plan_text.strip():
        return sections

    current = "preamble"
    buckets = {current: []}

    for line in plan_text.splitlines():
        heading = _match_heading(line)
        if heading:
            current = heading
            buckets.setdefault(current, [])
            # Keep any text written on the same line as the heading itself.
            inline = re.split(r"[\.\)\:\-–—]", _strip_markdown(line), maxsplit=1)
            if len(inline) > 1 and len(inline[1].strip()) > _MAX_HEADING_LEN:
                buckets[current].append(inline[1].strip())
            continue
        buckets.setdefault(current, []).append(line)

    for key, lines in buckets.items():
        sections[key] = "\n".join(lines).strip()

    return sections


def extract_list_items(section_text: str) -> list:
    """Pull bullet/numbered items out of a section.

    Falls back to sentence-splitting when the model wrote a prose paragraph
    instead of a list, so the Recommended Actions card is never empty when the
    section itself has content.
    """
    if not section_text:
        return []

    items = []
    for line in section_text.splitlines():
        match = _LIST_ITEM.match(line)
        if match:
            text = _strip_markdown(match.group(1))
            if text:
                items.append(text)
        elif items and line.strip() and not line.startswith(" " * 4):
            # Continuation of the previous wrapped bullet.
            items[-1] = f"{items[-1]} {line.strip()}"

    # A model that wrote every step on a single line yields one long "item";
    # split it back apart on its inline step numbers.
    if len(items) == 1 and len(_INLINE_STEP.findall(items[0])) >= 1:
        parts = [p.strip() for p in _INLINE_STEP.split(items[0]) if p.strip()]
        if len(parts) > 1:
            return parts

    if items:
        return items

    prose = " ".join(section_text.split())
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", prose) if s.strip()]
    return sentences


def extract_source_manual(references_text: str) -> dict:
    """Best-effort read of the manual name and page out of Section 6.

    The /iot-alert response does not return the retrieved manual name or page
    number as structured fields, so the only place this information exists is
    whatever the LLM cited in its Manual References section. Returns empty
    strings when nothing was cited, which the card renders as a "not cited"
    state rather than inventing a source.
    """
    result = {"name": "", "page": ""}
    if not references_text:
        return result

    # Manual names legitimately contain spaces ("Manual for Induction Motors and
    # Generators_EN.pdf"), so the match is greedy and any lead-in words the model
    # wrote before it are trimmed off afterwards.
    filename = re.search(r"([\w\-\. ]+\.pdf)", references_text, re.IGNORECASE)
    if filename:
        name = filename.group(1).strip()
        previous = None
        while name != previous:
            previous = name
            name = _CITATION_LEAD_IN.sub("", name).strip()
        result["name"] = name
    else:
        labelled = re.search(r"manual\s*[:\-]\s*([^\n,;]+)", references_text, re.IGNORECASE)
        if labelled:
            result["name"] = labelled.group(1).strip()

    page = re.search(r"pages?\s*[:\-]?\s*(\d+)", references_text, re.IGNORECASE)
    if page:
        result["page"] = page.group(1)

    return result


def _fmt_number(value) -> str:
    """Drop the trailing ".0" the backend's float fields would otherwise show,
    so a pressure of 120.0 reads as "120 psi" while 7.5 keeps its decimal."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _severity_badge(severity: str) -> str:
    css_class = {
        "critical": "badge-red",
        "high": "badge-red",
        "medium": "badge-amber",
        "low": "badge-green",
    }.get(str(severity).strip().lower(), "badge-gray")
    return f'<span class="badge {css_class}">{html.escape(str(severity).upper())}</span>'


def _card(title: str, icon: str, body_html: str, accent: str = "") -> str:
    accent_class = f" plan-card-{accent}" if accent else ""
    return (
        f'<div class="plan-card{accent_class}">'
        f'<div class="plan-card-title">{icon} {html.escape(title)}</div>'
        f'<div class="plan-card-body">{body_html}</div>'
        f"</div>"
    )


def _paragraph(text: str, empty_message: str) -> str:
    if not text or not text.strip():
        return f'<div class="plan-empty">{html.escape(empty_message)}</div>'
    escaped = html.escape(" ".join(text.split()))
    return f"<p>{escaped}</p>"


def _numbered_list(items: list, empty_message: str) -> str:
    if not items:
        return f'<div class="plan-empty">{html.escape(empty_message)}</div>'
    rows = "".join(
        f'<li><span class="plan-step-num">{i}</span>'
        f'<span class="plan-step-text">{html.escape(item)}</span></li>'
        for i, item in enumerate(items, start=1)
    )
    return f'<ol class="plan-step-list">{rows}</ol>'


def _bullet_list(items: list, empty_message: str) -> str:
    if not items:
        return f'<div class="plan-empty">{html.escape(empty_message)}</div>'
    rows = "".join(f"<li>{html.escape(item)}</li>" for item in items)
    return f'<ul class="plan-bullet-list">{rows}</ul>'


def _alert_rows(alert: dict) -> str:
    """Render the Equipment Alert card.

    IoTAlert carries vibration, pressure and severity, so they normally arrive
    in received_alert. Each row is still rendered only when its value is
    present, so an older or partial payload degrades to the fields it does have
    instead of erroring.
    """
    def measurement(key: str, unit: str):
        value = alert.get(key)
        return None if value is None else f"{_fmt_number(value)} {unit}"

    fields = [
        ("Machine ID", alert.get("machine_id")),
        ("Error Code", alert.get("error_code")),
        ("Temperature", measurement("temperature", "°C")),
        ("Vibration", measurement("vibration", "mm/s")),
        ("Pressure", measurement("pressure", "psi")),
    ]

    rows = "".join(
        f'<div class="plan-kv"><span class="plan-k">{html.escape(label)}</span>'
        f'<span class="plan-v">{html.escape(str(value))}</span></div>'
        for label, value in fields
        if value is not None and str(value).strip() != ""
    )

    severity = alert.get("severity")
    if severity:
        rows += (
            '<div class="plan-kv"><span class="plan-k">Severity</span>'
            f"<span class=\"plan-v\">{_severity_badge(severity)}</span></div>"
        )

    return rows or '<div class="plan-empty">No alert details available.</div>'


def _source_manual_card(source: dict) -> str:
    if not source.get("name"):
        return _card(
            "Source Manual",
            "\U0001f4d8",
            '<div class="plan-empty">The plan did not cite a specific manual page.</div>',
            accent="blue",
        )

    page_line = (
        f'<div class="plan-source-page">Page {html.escape(source["page"])}</div>'
        if source.get("page")
        else '<div class="plan-source-page">Page not specified</div>'
    )
    body = (
        f'<div class="plan-source-name">\U0001f4c4 {html.escape(source["name"])}</div>{page_line}'
    )
    return _card("Source Manual", "\U0001f4d8", body, accent="blue")


def _plan_details(sections: dict):
    """One expander holding everything that does not fit on the summary cards:
    the agent's SECTION 0/0B/0C verification checks, the full repair procedure,
    and the tools and spare parts lists."""
    blocks = [
        ("Error code verification", sections.get("verification", "")),
        ("System variant check", sections.get("variants", "")),
        ("Equipment scope check", sections.get("scope", "")),
        ("Full repair procedure", sections.get("procedure", "")),
        ("Required tools", sections.get("tools", "")),
        ("Required spare parts", sections.get("parts", "")),
    ]
    blocks = [(label, text) for label, text in blocks if text.strip()]
    if not blocks:
        return

    with st.expander("📋 Full plan details", expanded=False):
        for label, text in blocks:
            st.markdown(f"**{label}**")
            st.markdown(text)


def render_repair_plan(result=None, *, on_regenerate=None, key_prefix="repair_plan"):
    """Render Step 3 — AI Repair Plan.

    result:        the raw JSON dict returned by POST /iot-alert. Passing None
                   renders the waiting state, so the section can sit on the page
                   before an alert has been sent.
    on_regenerate: optional zero-argument callback wired to the Regenerate Plan
                   button. The button is hidden when no callback is supplied,
                   since re-sending the alert belongs to Step 2.
    key_prefix:    namespace for widget keys, in case the section is rendered
                   more than once on a page.
    """
    load_css("repair_plan.css")

    st.markdown(
        """
        <div class="workspace-step-header">
            <span class="step-number">3</span>
            <div>
                <div class="step-title">AI Repair Plan</div>
                <div class="step-subtitle">Recommended maintenance actions generated from the equipment alert and technical manuals.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not result:
        st.markdown(
            '<div class="plan-waiting">⏳ Send an IoT alert in Step 2 to generate a repair plan.</div>',
            unsafe_allow_html=True,
        )
        return

    alert = result.get("received_alert") or {}
    plan_text = result.get("repair_plan") or ""

    if not plan_text.strip():
        st.markdown(
            '<div class="plan-error">⚠️ The alert was received but the agent returned an empty repair plan.</div>',
            unsafe_allow_html=True,
        )
        return

    sections = parse_repair_plan(plan_text)
    # If the model ignored the section headings entirely, show whatever it did
    # write as the diagnosis rather than leaving every card empty.
    if not sections["diagnosis"].strip() and sections["preamble"].strip():
        sections["diagnosis"] = sections["preamble"]
    actions = extract_list_items(sections["procedure"])
    safety = extract_list_items(sections["safety"])
    source = extract_source_manual(sections["references"])

    resolved_key = f"{key_prefix}_resolved"
    if st.session_state.get(resolved_key):
        st.markdown(
            '<div class="plan-resolved-banner">✅ This alert has been marked as resolved.</div>',
            unsafe_allow_html=True,
        )

    col_alert, col_diag, col_actions, col_side = st.columns([1, 1.15, 1.3, 1])

    with col_alert:
        st.markdown(
            _card("Equipment Alert", "\U0001f6a8", _alert_rows(alert), accent="red"),
            unsafe_allow_html=True,
        )

    with col_diag:
        st.markdown(
            _card(
                "AI Diagnosis",
                "\U0001f916",
                _paragraph(sections["diagnosis"], "The plan did not include a diagnosis section."),
            ),
            unsafe_allow_html=True,
        )

    with col_actions:
        st.markdown(
            _card(
                "Recommended Actions",
                "\U0001f527",
                _numbered_list(actions, "The plan did not include a repair procedure."),
            ),
            unsafe_allow_html=True,
        )

    with col_side:
        st.markdown(
            _card(
                "Safety Precautions",
                "⚠️",
                _bullet_list(safety, "No safety precautions were listed."),
                accent="amber",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(_source_manual_card(source), unsafe_allow_html=True)

    _plan_details(sections)

    _render_actions(result, source, on_regenerate, key_prefix, resolved_key)


def _render_actions(result, source, on_regenerate, key_prefix, resolved_key):
    """The footer button row: Mark as Resolved / Regenerate Plan / View Manual."""
    columns = st.columns(3 if on_regenerate else 2)

    with columns[0]:
        already_resolved = st.session_state.get(resolved_key, False)
        label = "✓ Resolved" if already_resolved else "✓ Mark as Resolved"
        if st.button(label, key=f"{key_prefix}_resolve", use_container_width=True, disabled=already_resolved):
            st.session_state[resolved_key] = True
            st.rerun()

    next_col = 1
    if on_regenerate:
        with columns[next_col]:
            if st.button("↻ Regenerate Plan", key=f"{key_prefix}_regen", use_container_width=True):
                st.session_state[resolved_key] = False
                on_regenerate()
        next_col += 1

    with columns[next_col]:
        manual_name = source.get("name", "")
        if manual_name:
            # The view endpoint is keyed by manual name, which is the filename
            # without its .pdf extension.
            stem = manual_name[:-4] if manual_name.lower().endswith(".pdf") else manual_name
            st.link_button("\U0001f4c4 View Manual", get_view_url(stem), use_container_width=True)
        else:
            st.button(
                "\U0001f4c4 View Manual",
                key=f"{key_prefix}_view_disabled",
                use_container_width=True,
                disabled=True,
                help="The plan did not cite a specific manual.",
            )
