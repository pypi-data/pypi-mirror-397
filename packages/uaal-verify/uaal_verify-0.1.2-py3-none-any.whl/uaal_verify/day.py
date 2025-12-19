import os, json
from datetime import date
from .hashing import sha256_bytes

def verify_day(day: str | None = None, evidence_dir: str = "evidence") -> dict:
    day = day or date.today().isoformat()
    root_path = os.path.join(evidence_dir, "roots", f"{day}.json")

    if not os.path.exists(root_path):
        return {"date": day, "status": "FAIL", "reason": "missing_root"}

    with open(root_path) as f:
        stored = json.load(f)["root"]

    hashes = []
    for f in sorted(os.listdir(evidence_dir)):
        if f.endswith(".json") and f.startswith(day):
            with open(os.path.join(evidence_dir, f), "rb") as fh:
                hashes.append(sha256_bytes(fh.read()))

    if not hashes:
        return {"date": day, "status": "FAIL", "reason": "no_records"}

    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        hashes = [
            sha256_bytes((hashes[i] + hashes[i+1]).encode())
            for i in range(0, len(hashes), 2)
        ]

    computed = hashes[0]

    return {
        "date": day,
        "status": "OK" if computed == stored else "FAIL",
        "stored_root": stored,
        "computed_root": computed,
        "record_count": len(hashes)
    }
