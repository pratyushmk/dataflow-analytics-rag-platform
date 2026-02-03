
# Base ansewrs off the context from the retrieved docs
def build_prompt(context: str, question: str) -> str:
    return f"""
You are a system documentation assistant.

Answer the question ONLY using the context below.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{question}
""".strip()
