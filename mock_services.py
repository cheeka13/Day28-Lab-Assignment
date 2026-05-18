# mock_services.py
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import threading
import time

# 1. vLLM Server (port 8001)
vllm_app = FastAPI(title="Mock vLLM Server")

@vllm_app.get("/health")
def vllm_health():
    return {"status": "ok"}

@vllm_app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    model = body.get("model", "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4")
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "This is a high-quality mocked AI platform response explaining event-driven architecture and platform engineering."
                }
            }
        ],
        "model": model
    }

# 2. Embedding Server (port 8002)
embed_app = FastAPI(title="Mock Embedding Server")

@embed_app.post("/embed")
async def embed(request: Request):
    body = await request.json()
    texts = body.get("texts", [])
    embeddings = [[0.1] * 384 for _ in texts]
    return {"embeddings": embeddings}

# 3. Qdrant Server (port 6333)
qdrant_app = FastAPI(title="Mock Qdrant Server")

@qdrant_app.get("/healthz")
def qdrant_health():
    return Response(status_code=200)

@qdrant_app.get("/collections/documents")
def get_documents_collection():
    return {
        "result": {
            "status": "green",
            "points_count": 5,
            "vectors_count": 5
        }
    }

@qdrant_app.put("/collections/documents")
def recreate_collection():
    return {"result": True}

@qdrant_app.put("/collections/documents/points")
def upsert_points():
    return {"result": {"status": "completed"}}

@qdrant_app.post("/collections/documents/points/search")
async def search_points(request: Request):
    return {
        "result": [
            {
                "id": 1,
                "score": 0.99,
                "payload": {"id": "smoke_001", "text": "smoke test document"}
            }
        ]
    }

# 4. Prometheus Server (port 9090)
prometheus_app = FastAPI(title="Mock Prometheus")

@prometheus_app.get("/-/healthy")
def prom_healthy():
    return Response(status_code=200)

@prometheus_app.get("/api/v1/query")
def prom_query(query: str = ""):
    return {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": [
                {
                    "metric": {"job": "api-gateway"},
                    "value": [time.time(), "1"]
                }
            ]
        }
    }

# 5. Grafana Server (port 3000)
grafana_app = FastAPI(title="Mock Grafana")

@grafana_app.get("/api/health")
def grafana_health():
    return {"commit": "mock", "database": "ok", "version": "10.0.0"}

def run_server(app, port):
    try:
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
    except Exception as e:
        print(f"Error starting server on port {port}: {e}")

if __name__ == "__main__":
    threads = [
        threading.Thread(target=run_server, args=(vllm_app, 8001), daemon=True),
        threading.Thread(target=run_server, args=(embed_app, 8002), daemon=True),
        threading.Thread(target=run_server, args=(qdrant_app, 6333), daemon=True),
        threading.Thread(target=run_server, args=(prometheus_app, 9090), daemon=True),
        threading.Thread(target=run_server, args=(grafana_app, 3000), daemon=True),
    ]
    for t in threads:
        t.start()
    
    print("All mock services started on ports 8001, 8002, 6333, 9090, 3000.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping mock services.")
