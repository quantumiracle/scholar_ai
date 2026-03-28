from __future__ import annotations

import json
import sys


def main() -> int:
    payload = {"status": "placeholder", "message": "Implement OCR, reranking, or classifier jobs here."}
    sys.stdout.write(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
