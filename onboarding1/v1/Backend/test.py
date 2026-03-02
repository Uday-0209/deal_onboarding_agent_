from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import atexit

qdrant = QdrantClient(path="./qdrant_data")

atexit.register(qdrant.close)
