import json
import os
from flask import Flask, request, jsonify
import redis

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
MESSAGE    = os.getenv("MESSAGE", "Hello from todo-api (Python)")

# 建立 Redis 客户端（惰性：探针时再验证可用性）
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.get("/healthz")
def healthz():
    # 活性探针：进程起来即可 200
    return "ok", 200

@app.get("/readyz")
def readyz():
    # 就绪探针：Redis 通了才算 ready
    try:
        r.ping()
        
        return "ready", 200
    except Exception:
        return "not ready", 500

@app.get("/todos")
def list_todos():
    raw = r.get("todos")
    todos = json.loads(raw) if raw else []
    return jsonify(todos)

@app.post("/todos")
def add_todo():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "empty")
    raw = r.get("todos")
    todos = json.loads(raw) if raw else []
    todos.append({"id": int(__import__("time").time() * 1000), "text": text})
    r.set("todos", json.dumps(todos))
    return jsonify({"ok": True}), 201

@app.get("/cat")
def get_cat():
    cat_art = """
     /\\_/\\
    ( o.o )
     > ^ <
    """
    return cat_art.strip(), 200

@app.get("/")
def root():
    return MESSAGE, 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
