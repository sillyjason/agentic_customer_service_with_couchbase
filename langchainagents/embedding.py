from langchain_openai import OpenAIEmbeddings

embeddings_1024 = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1024)

# generate embedding
def create_openai_embeddings(input_message):
    return embeddings_1024.embed_documents([input_message])[0]

