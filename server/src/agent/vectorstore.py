import os

from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def get_vectorstore():
    backend = os.environ.get("VECTOR_STORE", "chroma").lower()

    if backend == "qdrant":
        from langchain_qdrant import QdrantVectorStore
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams

        client = QdrantClient(
            url=os.environ["QDRANT_URL"],
            api_key=os.environ["QDRANT_API_KEY"],
        )

        collection_name = "documents"
        existing = [c.name for c in client.get_collections().collections]
        if collection_name not in existing:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

        return QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )

    # default: chroma
    from langchain_chroma import Chroma

    return Chroma(
        collection_name="documents",
        embedding_function=embeddings,
        persist_directory="./data/chroma",
    )


def delete_by_source(source: str) -> None:
    """Delete all chunks that came from a given source file."""
    backend = os.environ.get("VECTOR_STORE", "chroma").lower()

    if backend == "qdrant":
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        client = QdrantClient(
            url=os.environ["QDRANT_URL"],
            api_key=os.environ["QDRANT_API_KEY"],
        )
        client.delete(
            collection_name="documents",
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="metadata.source",
                        match=MatchValue(value=source),
                    )
                ]
            ),
        )
    else:
        vs = get_vectorstore()
        vs._collection.delete(where={"source": source})
