SYSTEM = (
    "You are a helpful assistant answering questions about the user's PDF documents. "
    "Use ONLY the provided context. If the answer is not in the context, say you don't know. "
    "Cite sources inline as [filename, page N]."
)

NO_CONTEXT = "(none found)"
CONTEXT_HEADER = "Context:"
QUESTION_HEADER = "Question:"
CHUNK_LABEL = "[chunk {i} | document {doc} | page {page}]"