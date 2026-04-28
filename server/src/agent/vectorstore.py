import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, Filter, FieldCondition, MatchValue, VectorParams

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
COLLECTION = "documents"


def _client() -> QdrantClient:
    return QdrantClient(
        url=os.environ["QDRANT_URL"],
        api_key=os.environ["QDRANT_API_KEY"],
    )


def get_vectorstore() -> QdrantVectorStore:
    client = _client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
    return QdrantVectorStore(client=client, collection_name=COLLECTION, embedding=embeddings)


def delete_by_source(source: str) -> None:
    _client().delete(
        collection_name=COLLECTION,
        points_selector=Filter(
            must=[FieldCondition(key="metadata.source", match=MatchValue(value=source))]
        ),
    )
