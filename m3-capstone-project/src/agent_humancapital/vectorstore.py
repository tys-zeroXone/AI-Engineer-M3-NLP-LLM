from __future__ import annotations
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from agent_humancapital.config import SETTINGS
from agent_humancapital.llm import get_embeddings

def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=SETTINGS.QDRANT_URL, api_key=SETTINGS.QDRANT_API_KEY)

def get_vectorstore() -> QdrantVectorStore:
    return QdrantVectorStore(
        client=get_qdrant_client(),
        collection_name=SETTINGS.QDRANT_COLLECTION_NAME,
        embedding=get_embeddings(),
    )
