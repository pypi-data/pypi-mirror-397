import json
import hashlib
from datetime import datetime
from pathlib import Path

AUDIT_LOG_PATH = Path("aifoundary_audit.log")


def _hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


def emit_audit_event(
    *,
    decision,
    reason,
    prompt,
    context,
    policy_version="rag-policy-v1",
    sink="file"
):
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "decision": decision,
        "reason": reason,
        "policy_version": policy_version,
        "prompt_hash": _hash(prompt),
        "context_hash": _hash(context),
    }

    if sink == "file":
        with AUDIT_LOG_PATH.open("a") as f:
            f.write(json.dumps(event) + "\n")

    if sink == "uaal":
        try:
            import requests
            requests.post("http://localhost:8000/admin/emit", json=event, timeout=1)
        except Exception:
            pass

    return event
