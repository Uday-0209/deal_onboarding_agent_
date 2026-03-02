from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

import sys
from pathlib import Path

# Add parent directory to path BEFORE importing from Backend
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import from Backend (this will work both when imported and when run directly)
from Backend.embeddings import generate_embedding

# -------- Qdrant Embedded --------
qdrant = QdrantClient(
    path="./qdrant_data"  # local embedded storage
)

COLLECTION_NAME = "deal_summaries"
EMBEDDING_SIZE = 4096  # llama3.1 embedding size


def init_collection():
    collections = [c.name for c in qdrant.get_collections().collections]

    if COLLECTION_NAME not in collections:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_SIZE,
                distance=Distance.COSINE
            )
        )


init_collection()

def upsert_deal_summary(
    chat_id: str,
    summary: str,
    metadata: dict
):
    embedding = generate_embedding(summary)

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=chat_id,
                vector=embedding,
                payload={
                    "chat_id": chat_id,
                    "summary": summary,  # Store the summary too
                    **metadata
                }
            )
        ]
    )

def query_similar_deals(query: str, top_k: int = 3):
    query_embedding = generate_embedding(query)

    return qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k
    )

#------Manual_test------

if __name__ == "__main__":
    from Backend.summary_generator import generate_deal_summary

    intake = {
        "deal_type": "Real estate debt",
        "deal_size": "around 50 million USD",
        "geography": "Dubai",
        "sector": "Commercial real estate"
    }

    summary = generate_deal_summary(intake)

    upsert_deal_summary(
        chat_id="test-chat-001",
        summary=summary,
        metadata={
            "deal_type": intake["deal_type"],
            "geography": intake["geography"]
        }
    )

    results = query_similar_deals("Dubai real estate debt")

    if results:
        print("Top result:")
        print(f"Payload: {results[0].payload}")
        print(f"Score: {results[0].score}")
    else:
        print("No results found")