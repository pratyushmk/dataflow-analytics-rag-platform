from langchain_openai import OpenAIEmbeddings

# Use to switch models between OpenAI or soft embeddings.
def get_embeddings():
    return OpenAIEmbeddings()
