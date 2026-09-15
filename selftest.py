"""Replay every golden scenario through gate.py — no model, no network.

    python selftest.py

Prints one line per scenario and the same `GATE:` summary a real run would
print, then checks each verdict against fixtures/expected*.json. Exit 0
means the gate behaved exactly as documented; exit 1 names the scenario
that disagreed. Run this before trusting the gate, and again after any
edit to gate.py: the whole point of the file is that its behavior is
checkable without asking a model to promise anything.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import gate as gate_module

HERE = Path(__file__).parent
SUMMARY_RE = re.compile(
    r"^GATE: \d+ diffs / \d+ blocked "
    r"\(missing=\d+, fabricated=\d+, noop=\d+\) / resume-sha256=[0-9a-f]{12}$"
)
SETS = {
    "chinese fixtures": ("resume.md", "diffs.json", "allowlist.json", "expected.json"),
    "english fixtures": (
        "resume.en.md",
        "diffs.en.json",
        "allowlist.en.json",
        "expected.en.json",
    ),
}


def run_set(label: str, names: tuple[str, str, str, str]) -> list[str]:
    resume_text = (HERE / "fixtures" / names[0]).read_text(encoding="utf-8")
    diffs = json.loads((HERE / "fixtures" / names[1]).read_text(encoding="utf-8"))
    allowlist = gate_module.allowlist_corpus(
        (HERE / "fixtures" / names[2]).read_text(encoding="utf-8")
    )
    expected = json.loads((HERE / "fixtures" / names[3]).read_text(encoding="utf-8"))
    report = gate_module.run_gate(diffs, resume_text, allowlist)
    results = {r["diff_id"]: r for r in report["results"]}

    print(f"\n{label}")
    failures: list[str] = []
    for exp in expected["expectations"]:
        got = results.get(exp["diff_id"])
        if got is None:
            failures.append(f"{exp['diff_id']}: missing from gate output")
            print(f"  MISSING  {exp['diff_id']}")
            continue
        ok = (
            got["verdict"] == exp["verdict"]
            and got["reason"] == exp["reason"]
            and bool(got["salvaged"]) == exp["salvaged"]
        )
        flag = "ok  " if ok else "FAIL"
        note = " (quote salvaged)" if got["salvaged"] else ""
        detail = f" - {got['detail']}" if got["detail"] else ""
        print(
            f"  {flag} {got['diff_id']:<32} {got['verdict']}/{got['reason']}{note}{detail}"
        )
        if not ok:
            failures.append(
                f"{exp['diff_id']}: expected {exp['verdict']}/{exp['reason']} "
                f"salvaged={exp['salvaged']}, got {got['verdict']}/{got['reason']} "
                f"salvaged={got['salvaged']}"
            )
    summary = report["summary"]
    print(f"  {summary}")
    want = expected["summary"]
    if report["usable"] != want["usable"] or report["blocked"] != want["blocked"]:
        failures.append(
            f"{label}: counts {report['usable']}/{report['blocked']} != expected "
            f"{want['usable']}/{want['blocked']}"
        )
    if not SUMMARY_RE.match(summary):
        failures.append(f"{label}: summary line does not match the CLI contract")

    load_bearing = [
        exp["diff_id"]
        for exp in expected["expectations"]
        if "allowlist" in exp["diff_id"]
    ]
    for diff_id in load_bearing:
        item = next(d for d in diffs if d["diff_id"] == diff_id)
        without = gate_module.verdict(item, resume_text, "")
        if (without["verdict"], without["reason"]) != ("blocked", "fabricated"):
            failures.append(
                f"{diff_id}: passes without an allowlist, so the JD corpus is not load-bearing"
            )
        else:
            print(f"  ok   {diff_id:<32} blocked without the allowlist, as designed")
    return failures


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    print("true-tailor gate selftest — fixtures through the real gate.py, no LLM involved")
    failures: list[str] = []
    for label, names in SETS.items():
        failures += run_set(label, names)
    if failures:
        print("\nFAILED")
        for line in failures:
            print(f"  - {line}")
        return 1
    print("\nall scenarios ruled as documented")
    return 0


if __name__ == "__main__":
    sys.exit(main())
