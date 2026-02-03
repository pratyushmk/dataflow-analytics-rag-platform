from fastapi import APIRouter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI

from rag.embeddings import get_embeddings
from rag.prompt import build_prompt

router = APIRouter()

INDEX_PATH = "rag/index"

@router.get("/rag/search")
def rag_search(query: str):
    embeddings = get_embeddings()

    db = FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    docs = db.similarity_search(query, k=3)

    context = "\n\n".join(d.page_content for d in docs)

    llm = ChatOpenAI(temperature=0)

    prompt = build_prompt(context, query)
    response = llm.invoke(prompt)
    sources = list({d.metadata["source"] for d in docs})

    return {
        "query": query,
        "answer": response.content,
        "sources": sources
    }
