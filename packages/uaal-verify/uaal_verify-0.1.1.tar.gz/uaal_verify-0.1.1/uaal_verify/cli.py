import sys
from .day import verify_day
from .record import verify_record
from .range import verify_range

def main():
    if len(sys.argv) < 2:
        print("Usage: uaal-verify [day|record|range]")
        return

    cmd = sys.argv[1]

    if cmd == "day":
        print(verify_day(sys.argv[2] if len(sys.argv) > 2 else None))
    elif cmd == "record":
        print(verify_record(sys.argv[2]))
    elif cmd == "range":
        print(verify_range(sys.argv[2], sys.argv[3]))
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()
