import argparse
import json
from uaal_verify.day import verify_day
from uaal_verify.record import verify_record
from uaal_verify.range import verify_range


def main():
    parser = argparse.ArgumentParser(
        prog="uaal-verify",
        description="Independent verifier for UAAL decision evidence"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # day
    day = sub.add_parser("day", help="Verify all evidence for a given day")
    day.add_argument("date", help="YYYY-MM-DD")
    day.add_argument("--evidence-dir", default="evidence")

    # record
    record = sub.add_parser("record", help="Verify a single decision record")
    record.add_argument("decision_id")
    record.add_argument("--evidence-dir", default="evidence")

    # range
    rng = sub.add_parser("range", help="Verify evidence across a date range")
    rng.add_argument("start_date")
    rng.add_argument("end_date")
    rng.add_argument("--evidence-dir", default="evidence")

    args = parser.parse_args()

    if args.command == "day":
        result = verify_day(args.date, args.evidence_dir)
    elif args.command == "record":
        result = verify_record(args.decision_id, args.evidence_dir)
    elif args.command == "range":
        result = verify_range(args.start_date, args.end_date, args.evidence_dir)
    else:
        parser.print_help()
        return 1

    print(json.dumps(result, indent=2))
    return 0
