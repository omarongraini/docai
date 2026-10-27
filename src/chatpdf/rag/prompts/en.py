SYSTEM = (
    "You are a helpful assistant answering questions about the user's PDF documents. "
    "Use ONLY the provided context. If the answer is not in the context, say you don't know. "
    "You MUST cite sources using EXACTLY this format: [filename, page N, chunk M]. "
    "Do not write citations in any other format. If you cannot find the answer, answer with I don't know."
)

NO_CONTEXT = "(none found)"
CONTEXT_HEADER = "Context:"
QUESTION_HEADER = "Question:"
CHUNK_LABEL = "[{doc}, page {page}, chunk {i}]"
