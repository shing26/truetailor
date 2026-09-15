"""Apply gate-cleared diffs to a candidate copy of the resume.

Step 4 of the true-tailor loop, as code: this re-runs the gate itself and
refuses to write any diff the gate did not clear, so "I applied the
suggestions" cannot mean "I applied the ones that were blocked". Salvaged
diffs are applied against the corrected source line, not the model's
misremembered quote.

    python apply.py --resume resume.md --diffs diffs.json \
        --allowlist gap.json --accept <diff_id> [--accept <diff_id> ...] \
        --out resume.r1.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import gate as gate_module


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--resume", required=True)
    parser.add_argument("--diffs", required=True)
    parser.add_argument("--allowlist", default="")
    parser.add_argument("--accept", action="append", default=[], required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    try:
        resume_text = Path(args.resume).read_text(encoding="utf-8")
        raw = json.loads(Path(args.diffs).read_text(encoding="utf-8"))
        allow = (
            gate_module.allowlist_corpus(Path(args.allowlist).read_text(encoding="utf-8"))
            if args.allowlist
            else ""
        )
    except (OSError, ValueError) as exc:
        print(f"apply error: {exc}", file=sys.stderr)
        return 2

    diffs = raw.get("diffs") if isinstance(raw, dict) else raw
    if not isinstance(diffs, list):
        print('apply error: diffs must be a JSON list or {"diffs": [...]}', file=sys.stderr)
        return 2

    report = gate_module.run_gate(diffs, resume_text, allow)
    cleared = {r["diff_id"]: r for r in report["results"] if r["verdict"] == "usable"}
    payload = {str(item.get("diff_id")): item for item in diffs}
    text = resume_text
    applied = 0
    for diff_id in args.accept:
        result = cleared.get(diff_id)
        if result is None:
            print(f"refused {diff_id}: not gate-cleared this run")
            continue
        original = result["original"]
        proposed = str(payload.get(diff_id, {}).get("proposed") or "")
        if not original or original not in text:
            print(f"refused {diff_id}: source line not found in the resume")
            continue
        if not proposed.strip():
            print(f"refused {diff_id}: empty proposed text")
            continue
        text = text.replace(original, proposed, 1)
        applied += 1
        note = " (salvaged quote)" if result["salvaged"] else ""
        print(f"applied {diff_id}{note}")
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"{applied}/{len(args.accept)} accepted diffs -> {args.out}")
    print(report["summary"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
