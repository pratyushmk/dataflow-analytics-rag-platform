from pathlib import Path
from langchain_core.documents import Document

# Loads markdown / text files and converts them to LangChain Document objects
def load_documents(docs_path: str) -> list[Document]:
    documents = []

    for file in Path(docs_path).glob("*.md"):
        text = file.read_text()
        documents.append(
            Document(
                page_content=text,
                metadata={"source": file.name}
            )
        )

    return documents
