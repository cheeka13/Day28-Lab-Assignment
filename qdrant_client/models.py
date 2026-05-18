# qdrant_client/models.py

class Distance:
    COSINE = "Cosine"

class VectorParams:
    def __init__(self, size, distance):
        self.size = size
        self.distance = distance

class PointStruct:
    def __init__(self, id, vector, payload):
        self.id = id
        self.vector = vector
        self.payload = payload
