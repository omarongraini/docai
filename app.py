import re

import streamlit as st

from chatpdf.factories import get_document_store
from chatpdf.rag.chat import retrieve, stream_from_chunks
from chatpdf.rag.ingest import ingest_pdf

st.set_page_config(page_title="Chat with PDF", page_icon="📄", layout="wide")

st.markdown(
    """
    <style>
    div[data-testid="stHorizontalBlock"] { gap: 0.4rem !important; }
    div[data-testid="stPopover"] button {
        padding: 0.25rem 0.6rem !important;
        white-space: nowrap !important;
        font-size: 0.85rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _is_arabic(text: str) -> bool:
    return any("\u0600" <= c <= "\u06ff" for c in text)


def _render_html(content: str, lang: str) -> str:
    if lang == "ar":
        return f"<div dir='rtl' style='text-align: right; unicode-bidi: plaintext;'>{content}</div>"
    return f"<div style='text-align: left;'>{content}</div>"


def _filter_cited_chunks(chunks: list, response: str) -> list:
    if not chunks or not response:
        return chunks
    cited_pages = {int(m) for m in re.findall(r"page\s+(\d+)", response, re.IGNORECASE)}
    cited_pages.update(int(m) for m in re.findall(r"صفحة\s+(\d+)", response))
    if not cited_pages:
        return []
    return [c for c in chunks if c.page in cited_pages]


if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("📄 Documents")
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded is not None and st.button("Ingest", type="primary"):
        with st.spinner(f"Ingesting {uploaded.name}…"):
            try:
                doc = ingest_pdf(uploaded.name, uploaded.getvalue())
                st.success(f"Ingested {doc.filename}")
                st.rerun()
            except Exception as e:  # noqa: BLE001 — UI boundary, surface any failure
                st.error(f"Ingest failed: {e}")

    st.divider()
    try:
        docs = get_document_store().list()
    except Exception as e:  # noqa: BLE001 — UI boundary, surface any failure
        docs = []
        st.caption(f"Could not load documents: {e}")

    if docs:
        doc_options = {d.id: f"{d.filename}  ({d.id[:8]}…)" for d in docs}
        selected_ids = st.multiselect(
            "Search in",
            options=list(doc_options.keys()),
            default=list(doc_options.keys()),
            format_func=lambda x: doc_options[x],
        )
    else:
        selected_ids = []
        st.caption("No documents yet.")

    try:
        filename_map = {d.id: d.filename for d in get_document_store().list()}
    except Exception as e:  # noqa: BLE001 — UI boundary, surface any failure
        filename_map = {}
        st.caption(f"⚠️ Could not load filenames: {e}")

st.title("Chat with your PDFs")

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(
            _render_html(msg["content"], msg.get("language", "en")),
            unsafe_allow_html=True,
        )

if prompt := st.chat_input("Ask a question about your documents…"):
    lang = "ar" if _is_arabic(prompt) else "en"
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "language": lang}
    )

    with st.chat_message("user"):
        st.markdown(_render_html(prompt, lang), unsafe_allow_html=True)

    with st.chat_message("assistant"):
        chunks = []
        response = ""

        try:
            # 1. Search phase
            with st.spinner("🔍 Searching documents…"):
                chunks = retrieve(prompt, document_ids=selected_ids)

            # 2. Generation phase
            # Create one empty placeholder for the text to stream into
            placeholder = st.empty()

            # Show the "Generating..." message inside the placeholder
            placeholder.markdown("🤖 Generating answer…")

            tokens = []
            for token in stream_from_chunks(
                prompt, chunks, language=lang, filenames=filename_map
            ):
                tokens.append(token)
                # Overwrite the placeholder with the growing text + a blinking cursor
                placeholder.markdown(
                    _render_html("".join(tokens) + "▌", lang), unsafe_allow_html=True
                )

            response = "".join(tokens)
            # Final render (remove the cursor)
            placeholder.markdown(_render_html(response, lang), unsafe_allow_html=True)

        except Exception as e:  # noqa: BLE001 — UI boundary, surface any failure
            response = f"⚠️ Error: {e}"
            st.markdown(response)

        chunks = _filter_cited_chunks(chunks, response)

        if chunks:
            widths = [2] * len(chunks) + [10]
            cols = st.columns(widths, gap="small")
            for i, c in enumerate(chunks):
                fname = filename_map.get(c.document_id, c.document_id[:8])
                with cols[i], st.popover(f"📎 {fname} · p{c.page}"):
                    st.caption(f"score {c.score:.2f} · chunk {c.chunk_index}")
                    st.text(c.content)

    st.session_state.messages.append(
        {"role": "assistant", "content": response, "language": lang}
    )
