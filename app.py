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

if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "en"

with st.sidebar:
    st.header("📄 Documents")

    lang = st.selectbox(
        "Language",
        options=["en", "ar"],
        index=["en", "ar"].index(st.session_state.language),
        format_func=lambda x: {"en": "English", "ar": "العربية"}[x],
    )
    st.session_state.language = lang

    uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded is not None:
        if st.button("Ingest", type="primary"):
            with st.spinner(f"Ingesting {uploaded.name}…"):
                try:
                    doc = ingest_pdf(uploaded.name, uploaded.getvalue())
                    st.success(f"Ingested {doc.filename}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ingest failed: {e}")

    st.divider()
    try:
        docs = get_document_store().list()
    except Exception as e:
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
    except Exception:
        filename_map = {}

st.title("Chat with your PDFs")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("language") == "ar":
            st.markdown(
                f"<div dir='rtl' style='text-align: right; unicode-bidi: plaintext;'>"
                f"{msg['content']}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about your documents…"):
    lang = st.session_state.language
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "language": lang}
    )
    with st.chat_message("user"):
        if lang == "ar":
            st.markdown(
                f"<div dir='rtl' style='text-align: right; unicode-bidi: plaintext;'>"
                f"{prompt}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(prompt)

    with st.chat_message("assistant"):
        chunks = []
        response = ""
        status_ph = st.empty()
        try:
            status_ph.status("🔍 Searching documents…", expanded=False)
            chunks = retrieve(prompt, document_ids=selected_ids)
            status_ph.status("🤖 Generating answer…", expanded=False)

            if lang == "ar":
                tokens = []
                for token in stream_from_chunks(prompt, chunks, language="ar"):
                    if not tokens:
                        status_ph.empty()
                    tokens.append(token)
                response = "".join(tokens)
                st.markdown(
                    f"<div dir='rtl' style='text-align: right; unicode-bidi: plaintext;'>"
                    f"{response}</div>",
                    unsafe_allow_html=True,
                )
            else:
                def _stream():
                    first = True
                    for token in stream_from_chunks(prompt, chunks, language="en"):
                        if first:
                            status_ph.empty()
                            first = False
                        yield token

                response = st.write_stream(_stream())
        except Exception as e:
            status_ph.empty()
            response = f"⚠️ Error: {e}"
            st.markdown(response)

        if chunks:
            widths = [2] * len(chunks) + [10]
            cols = st.columns(widths, gap="small")
            for i, c in enumerate(chunks):
                fname = filename_map.get(c.document_id, c.document_id[:8])
                with cols[i]:
                    with st.popover(f"📎 {fname} · p{c.page}"):
                        st.caption(f"score {c.score:.2f} · chunk {c.chunk_index}")
                        st.text(c.content)

    st.session_state.messages.append(
        {"role": "assistant", "content": response, "language": lang}
    )