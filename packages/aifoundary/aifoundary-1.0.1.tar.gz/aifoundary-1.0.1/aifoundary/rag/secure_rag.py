from aifoundary.policy.loader import load_policy
from aifoundary.audit.signed_log import append_signed_event
from aifoundary.rag.coverage import check_coverage
import re


def _redact(text: str) -> str:
    patterns = [
        r"\b\d{3}-\d{2}-\d{4}\b",
        r"\b\d{4}-\d{4}-\d{4}-\d{4}\b",
    ]
    for p in patterns:
        text = re.sub(p, "[REDACTED]", text)
    return text


def validate_rag(
    prompt: str,
    contexts: list[str],
    *,
    policy_path: str = "rag_policy.yaml",
    mode: str = "strict",
):
    policy = load_policy(policy_path)
    rules = policy["rules"]

    prompt_l = prompt.lower()
    contexts_l = [c.lower() for c in contexts]
    joined_context = " ".join(contexts_l)

    decision = {"allowed": True, "reason": "OK"}

    # 1️⃣ Prompt override
    if rules.get("block_prompt_override") and any(
        x in prompt_l for x in ["ignore context", "ignore previous", "disregard"]
    ):
        decision = {"allowed": False, "reason": "Prompt override"}

    # 2️⃣ Require context
    elif rules.get("require_context") and not contexts:
        decision = {"allowed": False, "reason": "No context provided"}

    # 3️⃣ PII handling
    elif rules.get("block_pii") and any(
        x in joined_context for x in ["ssn", "credit card", "aadhaar", "4111"]
    ):
        if rules.get("allow_redaction") and mode == "redact":
            decision = {
                "allowed": True,
                "reason": "PII redacted",
                "redacted_contexts": [_redact(c) for c in contexts],
            }
        else:
            decision = {"allowed": False, "reason": "PII detected"}

    # 4️⃣ Explainable coverage check
    else:
        coverage = check_coverage(
            prompt,
            contexts,
            min_ratio=rules.get("min_coverage_ratio", 0.3),
        )

        if not coverage["ok"]:
            decision = {
                "allowed": False,
                "reason": "Insufficient context coverage",
                "coverage": coverage,
            }

    append_signed_event(
        {
            "decision": decision["allowed"],
            "reason": decision["reason"],
            "policy_version": policy["version"],
        }
    )

    return decision
