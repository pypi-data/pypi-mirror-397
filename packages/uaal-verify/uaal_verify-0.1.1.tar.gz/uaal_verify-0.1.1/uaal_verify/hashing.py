import hashlib
import json

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_json(obj: dict) -> str:
    raw = json.dumps(obj, sort_keys=True).encode()
    return sha256_bytes(raw)
