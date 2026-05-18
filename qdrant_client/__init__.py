# qdrant_client/__init__.py

class QdrantClient:
    def __init__(self, host=None, port=None, **kwargs):
        self.host = host
        self.port = port

    def recreate_collection(self, collection_name, vectors_config, **kwargs):
        print(f"[Mock QdrantClient] Recreated collection: {collection_name}")
        return True

    def upsert(self, collection_name, points, **kwargs):
        print(f"[Mock QdrantClient] Upserted {len(points)} points into {collection_name}")
        return True
