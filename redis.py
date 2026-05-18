# redis.py mock
import json
import os

REDIS_FILE = os.path.join(os.path.dirname(__file__), "redis_db.json")

def _read_db():
    if os.path.exists(REDIS_FILE):
        try:
            with open(REDIS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _write_db(db):
    try:
        with open(REDIS_FILE, "w") as f:
            json.dump(db, f)
    except Exception:
        pass

class Redis:
    def __init__(self, host=None, port=None, decode_responses=False, **kwargs):
        self.host = host
        self.port = port
        self.decode_responses = decode_responses

    def ping(self):
        return True

    def set(self, key, value, **kwargs):
        db = _read_db()
        db[key] = value
        _write_db(db)
        return True

    def get(self, key):
        db = _read_db()
        return db.get(key)

    def keys(self, pattern):
        db = _read_db()
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return [k for k in db.keys() if k.startswith(prefix)]
        return list(db.keys())
