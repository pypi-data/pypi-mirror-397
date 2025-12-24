import json
import hashlib
from datetime import datetime
from pathlib import Path

AUDIT_PATH = Path("aifoundary_audit.chain")


def _hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def append_signed_event(event: dict):
    prev_hash = None

    if AUDIT_PATH.exists():
        last = AUDIT_PATH.read_text().strip().splitlines()[-1]
        prev_hash = json.loads(last)["event_hash"]

    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "prev_hash": prev_hash,
    }

    serialized = json.dumps(payload, sort_keys=True)
    payload["event_hash"] = _hash(serialized)

    with AUDIT_PATH.open("a") as f:
        f.write(json.dumps(payload) + "\n")

    return payload
