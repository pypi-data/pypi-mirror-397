import json, os
from .hashing import sha256_json

def verify_record(record_id: str, evidence_dir: str = "evidence") -> dict:
    for fname in os.listdir(evidence_dir):
        if record_id in fname and fname.endswith(".json"):
            path = os.path.join(evidence_dir, fname)
            with open(path) as f:
                record = json.load(f)

            computed = sha256_json(record)
            stored = record.get("hash")

            if stored and stored != computed:
                return {
                    "record_id": record_id,
                    "status": "FAIL",
                    "reason": "hash_mismatch"
                }

            return {
                "record_id": record_id,
                "status": "OK",
                "timestamp": record.get("timestamp"),
                "hash": computed
            }

    return {
        "record_id": record_id,
        "status": "FAIL",
        "reason": "record_not_found"
    }
