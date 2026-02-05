from __future__ import annotations
import os
import logging
import pandas as pd
from uuid import uuid4
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings

load_dotenv()
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION = os.getenv("QDRANT_COLLECTION_NAME", "resumes_collection")

if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY")
if not QDRANT_URL or not QDRANT_API_KEY:
    raise ValueError("Missing QDRANT_URL / QDRANT_API_KEY")

def main():
    excel_path = "dataset/dataset.xlsx"
    df = pd.read_excel(excel_path)

    # Adjust these if your columns differ
    text_col = "Resume_str"
    cat_col = "Category"

    docs = []
    for idx, row in df.iterrows():
        content = str(row.get(text_col, "") or "")
        if not content.strip():
            continue
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "row_index": int(idx),
                    "category": str(row.get(cat_col, "Unknown")),
                    "source": os.path.basename(excel_path),
                },
            )
        )

    logging.info(f"Loaded {len(docs)} documents from Excel")

    client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=True,
    timeout=120,
    )  

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)

    # Create collection if needed
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        # Common dimension for text-embedding-3-small is often 1536; adjust if needed
        dim = 1536
        logging.info(f"Creating collection={COLLECTION} dim={dim}")
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

    vs = QdrantVectorStore(client=client, collection_name=COLLECTION, embedding=embeddings)
    ids = [str(uuid4()) for _ in range(len(docs))]
    vs.add_documents(documents=docs, ids=ids)
    logging.info("Ingestion complete")

if __name__ == "__main__":
    main()
