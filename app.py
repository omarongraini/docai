import streamlit as st

from chatpdf.factories import get_document_store
from chatpdf.rag.chat import retrieve, stream_from_chunks
from chatpdf.rag.ingest import ingest_pdf

st.set_page_config(page_title="Chat with PDF", page_icon="📄", layout="wide")

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
        try:
            with st.status("🔍 Searching documents…", expanded=False) as status:
                chunks = retrieve(prompt, document_ids=selected_ids)
                status.update(label=f"✅ Found {len(chunks)} chunks", state="complete")

            if lang == "ar":
                with st.spinner("🤖 Generating answer…"):
                    response = "".join(
                        stream_from_chunks(prompt, chunks, language="ar")
                    )
                st.markdown(
                    f"<div dir='rtl' style='text-align: right; unicode-bidi: plaintext;'>"
                    f"{response}</div>",
                    unsafe_allow_html=True,
                )
            else:
                response = st.write_stream(
                    stream_from_chunks(prompt, chunks, language="en")
                )
        except Exception as e:
            response = f"⚠️ Error: {e}"
            st.markdown(response)

        if chunks:
            with st.expander(f"📎 Sources ({len(chunks)})"):
                for c in chunks:
                    st.caption(
                        f"• doc `{c.document_id[:8]}…` page {c.page} "
                        f"(score {c.score:.2f})"
                    )
                    st.text(c.content)

    st.session_state.messages.append(
        {"role": "assistant", "content": response, "language": lang}
    )