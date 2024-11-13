from langchain_qdrant import QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from langchain_community.embeddings import (
    HuggingFaceInferenceAPIEmbeddings,
)
from langchain.schema import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from langchain.retrievers import BM25Retriever, EnsembleRetriever

hf_embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key="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",
    model_name="deepvk/USER-bge-m3"
)

docs = [
    Document(page_content="This is a sample document about weather."),
    Document(page_content="Ваша кредитная карта была утерена"),
    Document(page_content="Томас не нашел друзей"),
]

client = QdrantClient(location='0.0.0.0', port=6654)
vector_store = QdrantVectorStore(
    client=client,
    collection_name="med_db",
    embedding=hf_embeddings
)

text_docs = [doc.page_content for doc in docs]

bm25_retriever = BM25Retriever.from_texts(text_docs)
bm25_retriever.k = 1

vectorstore_retriever = vector_store.as_retriever(search_kwargs={"k": 1})
ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, vectorstore_retriever], weights=[0.5, 0.5])

relevant_docs = ensemble_retriever.get_relevant_documents("томас нашел друзей?")


for idx, doc in enumerate(relevant_docs):
    print(f"Результат {idx + 1}:\n{doc.page_content}\n")

# docs = ensemble_retriever.invoke("Who am I")
# print(docs)


# query = "What is weather tommorrow ?"
# found_docs = vector_store.similarity_search(query, k=1)
# print(found_docs[0].page_content)