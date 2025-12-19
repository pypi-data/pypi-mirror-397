from datetime import date, timedelta
from .day import verify_day

def verify_range(start_date: str, end_date: str, evidence_dir: str = "evidence") -> dict:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    failures = []

    cur = start
    while cur <= end:
        res = verify_day(cur.isoformat(), evidence_dir)
        if res["status"] != "OK":
            failures.append(res)
        cur += timedelta(days=1)

    return {
        "status": "OK" if not failures else "FAIL",
        "days_verified": (end - start).days + 1,
        "failed_days": failures
    }
