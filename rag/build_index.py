from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from doc_loader import load_documents
from embeddings import get_embeddings

DOCS_PATH = "docs/"
INDEX_PATH = "rag/index"

def main():

    docs = load_documents(DOCS_PATH)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(docs)

    embeddings = get_embeddings()
    db = FAISS.from_documents(chunks, embeddings)
    print(f"Indexed {len(chunks)} chunks")

    db.save_local(INDEX_PATH)

if __name__ == "__main__":
    main()
