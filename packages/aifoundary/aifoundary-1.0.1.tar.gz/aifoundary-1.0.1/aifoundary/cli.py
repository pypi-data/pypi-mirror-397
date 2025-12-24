import argparse
import json
from pathlib import Path

from aifoundary.rag.secure_rag import validate_rag
from aifoundary.rag.auto_retry import validate_with_retry
from aifoundary.policy.loader import load_policy


def run_rag_check(prompt_path: Path, context_path: Path, json_mode: bool, retry: bool):
    prompt = prompt_path.read_text()
    context = context_path.read_text()

    contexts = [context]

    if retry:
        verdict = validate_with_retry(
            prompt,
            contexts,
            policy_path="rag_policy.yaml",
        )
    else:
        verdict = validate_rag(
            prompt,
            contexts,
            policy_path="rag_policy.yaml",
        )

    if json_mode:
        print(json.dumps(verdict))
    else:
        print("RAG Compliance Verdict")
        print("----------------------")
        print(f"Allowed: {verdict['allowed']}")
        print(f"Reason: {verdict['reason']}")

        if "coverage" in verdict:
            print("Coverage:", verdict["coverage"])

        if "suggested_prompt" in verdict:
            print("Suggested prompt:", verdict["suggested_prompt"])


def run_policy_simulation(prompts_path: Path, context_path: Path):
    prompts = prompts_path.read_text().splitlines()
    context = context_path.read_text()
    contexts = [context]

    policy = load_policy("rag_policy.yaml")

    results = {
        "total": len(prompts),
        "allowed": 0,
        "blocked": 0,
        "blocked_reasons": {},
    }

    for p in prompts:
        verdict = validate_rag(p, contexts, policy_path="rag_policy.yaml")
        if verdict["allowed"]:
            results["allowed"] += 1
        else:
            results["blocked"] += 1
            r = verdict["reason"]
            results["blocked_reasons"][r] = results["blocked_reasons"].get(r, 0) + 1

    print(json.dumps({
        "policy_version": policy["version"],
        "results": results
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(prog="aifoundary")
    sub = parser.add_subparsers(dest="cmd")

    rag = sub.add_parser("rag-check", help="Validate RAG prompt + context")
    rag.add_argument("prompt")
    rag.add_argument("context")
    rag.add_argument("--json", action="store_true")
    rag.add_argument("--retry", action="store_true", help="Auto-rewrite + retry")

    sim = sub.add_parser("policy-simulate", help="Simulate policy over prompts")
    sim.add_argument("prompts")
    sim.add_argument("context")

    args = parser.parse_args()

    if args.cmd == "rag-check":
        run_rag_check(Path(args.prompt), Path(args.context), args.json, args.retry)
    elif args.cmd == "policy-simulate":
        run_policy_simulation(Path(args.prompts), Path(args.context))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
