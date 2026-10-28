import re
import time

import streamlit as st

from docai.factories import get_document_store
from docai.features.chat import retrieve, stream_from_chunks
from docai.logger import logger
from docai.rag.ingest import ingest_pdf

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
    [data-testid="stMarkdownContainer"] { overflow: visible !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _is_arabic(text: str) -> bool:
    return any("\u0600" <= c <= "\u06ff" for c in text)


def _render_html(content: str, lang: str) -> str:
    if lang == "ar":
        return f"<div dir='rtl' style='text-align: right; unicode-bidi: plaintext; white-space: pre-wrap;'>{content}</div>"
    return f"<div style='text-align: left; white-space: pre-wrap;'>{content}</div>"


def _filter_cited_chunks(chunks: list, response: str) -> list:
    if not chunks or not response:
        return chunks

    brackets = re.findall(r"\[(.*?)\]", response)
    cited = set()

    for text in brackets:
        p_match = re.search(r"(?:page|صفحة)\s*(\d+)", text, re.IGNORECASE)
        c_match = re.search(r"(?:chunk|مقطع)\s*(\d+)", text, re.IGNORECASE)
        if p_match and c_match:
            cited.add((int(p_match.group(1)), int(c_match.group(1))))

    if not cited:
        return []

    seen = set()
    result = []
    for c in chunks:
        if (c.page, c.chunk_index) in cited:
            sig = (c.document_id, c.page, c.chunk_index)
            if sig not in seen:
                seen.add(sig)
                result.append(c)
    return result


if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("📄 Documents")
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded is not None and st.button("Ingest", type="primary"):
        with st.spinner(f"Processing {uploaded.name}…"):
            try:
                doc = ingest_pdf(uploaded.name, uploaded.getvalue())
                if doc.filename != uploaded.name:
                    st.info(f"File already exists as '{doc.filename}'.")
                else:
                    st.success(f"Ingested {doc.filename}")
                    st.rerun()
            except Exception as e:  # noqa: BLE001 (UI boundary: catch all to prevent app crash) # noqa: BLE001 (UI boundary: catch all to prevent app crash)
                st.error(f"Ingest failed: {e}")

    st.divider()
    try:
        docs = get_document_store().list()
    except Exception as e:  # noqa: BLE001 (UI boundary: catch all to prevent app crash) # noqa: BLE001 (UI boundary: catch all to prevent app crash)
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
    except Exception as e:  # noqa: BLE001 (UI boundary: catch all to prevent app crash) # noqa: BLE001 (UI boundary: catch all to prevent app crash)
        filename_map = {}
        st.caption(f"⚠️ Could not load filenames: {e}")

st.title("Chat with your PDFs")

# Render History (Only successful messages are saved here)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(
            _render_html(msg["content"], msg.get("language", "en")),
            unsafe_allow_html=True,
        )

if not selected_ids:
    st.warning(
        "⚠️ Please select at least one document in the sidebar to start chatting."
    )
else:
    if prompt := st.chat_input("Ask a question about your documents…"):
        logger.info(f"=== User asked: {prompt!r} ===")

        lang = "ar" if _is_arabic(prompt) else "en"
        # Save the user's prompt
        st.session_state.messages.append(
            {"role": "user", "content": prompt, "language": lang}
        )

        with st.chat_message("user"):
            st.markdown(_render_html(prompt, lang), unsafe_allow_html=True)

        with st.chat_message("assistant"):
            chunks = []
            response = ""
            start_time = time.time()

            try:
                with st.spinner("🔍 Searching and generating…"):
                    chunks = retrieve(prompt, document_ids=selected_ids)
                    # Buffer the stream in memory to prevent mid-stream crashes
                    tokens = list(
                        stream_from_chunks(
                            prompt, chunks, language=lang, filenames=filename_map
                        )
                    )
                    response = "".join(tokens)
            except Exception as e:  # noqa: BLE001 (UI boundary: catch all to prevent app crash)
                logger.error(f"Streaming error: {e}")
                response = f"⚠️ Error: {e}"

            # If it's an error, show the red box. If not, show the answer.
            if response.startswith("⚠️ Error:"):
                st.error(response)
            else:
                st.markdown(_render_html(response, lang), unsafe_allow_html=True)

                elapsed = time.time() - start_time
                chunks = _filter_cited_chunks(chunks, response)

                if chunks:
                    widths = [2] * len(chunks) + [10]
                    cols = st.columns(widths, gap="small")
                    for i, c in enumerate(chunks):
                        fname = filename_map.get(c.document_id, c.document_id[:8])
                        with cols[i], st.popover(f"📎 {fname} · p{c.page}"):
                            st.caption(f"score {c.score:.2f} · chunk {c.chunk_index}")
                            st.text(c.content)

                st.caption(f"⏱️ {elapsed:.2f}s")

        # SAVE TO HISTORY: This keeps the error on the screen!
        st.session_state.messages.append(
            {"role": "assistant", "content": response, "language": lang}
        )
