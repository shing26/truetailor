# Gate contract

`gate.py` is the part of this project that makes a claim checkable, so its input
and output shape is a contract, not an implementation detail.

## Invariants

1. **One file, standard library only.** No third-party imports, no network, no
   filesystem outside the paths you pass it, no reading of the resume except
   through `--resume`. It must run on any `python3` on any machine that has the
   file.
2. **Fail closed.** Anything the gate cannot place gets `blocked`. The gate has
   no flag that weakens this, and there is deliberately no "strictness" knob.
3. **Deterministic.** Same resume, same diffs, same allowlist, same verdicts and
   the same `resume-sha256`. Only the `ts` field in the log moves.
4. **The model is never the judge.** A suggestion is `usable` because the gate
   said so in this run, against this resume file.

## Input

```
python gate.py --resume resume.md --diffs diffs.json \
  [--allowlist gap.json] [--log run.jsonl] [--round N] [--trigger eval:roundN-1]
```

- `--resume` - UTF-8 plain text or Markdown. This is the only supported fact
  source about the candidate.
- `--diffs` - JSON list, or `{"diffs": [...]}`. Each item:
  `diff_id`, `type` (`modify` | `add` | `remove`), `section`, `original`,
  `proposed`, `provenance`, `reason`, `confidence`. Unknown types are treated as
  `modify`; an `add` must put its supporting sentence in `original`.
- `--allowlist` - optional. Parsed as the gap report (`missing_keywords`,
  `misaligned_emphasis`, `strength_matches`, `business_scenarios`,
  `jd_context`) when it is JSON with those keys, otherwise taken as raw text.
  It is the only route by which a word that is not in the resume may appear in
  `proposed`, so it must contain JD-side vocabulary and never resume-side copies.

## Output

stdout, one line per diff in input order:

```
OK  <diff_id> [<type>/<reason>] <detail>
BLOCK <diff_id> [<type>/<reason>] <detail>
```

then exactly one machine-readable summary line:

```
GATE: <n> diffs / <k> blocked (missing=<a>, fabricated=<b>, noop=<c>) / resume-sha256=<12 hex>
```

Exit `0` when the run completed, including when everything was blocked; `2` for
usage or IO errors, with `gate error: ...` on stderr.

| `reason` | meaning |
|---|---|
| `verified` | usable: provenance located, content sourced, not a no-op |
| `missing` | the quote cannot be located in the resume, or an `add` has no supporting sentence |
| `fabricated` | `proposed` carries a number or a name with no source in resume + anchor + allowlist |
| `noop` | `modify`/`remove` whose proposed text equals its original once stripped |

`salvaged` is not a verdict: it marks a diff whose misquoted provenance was
recovered by fuzzy matching, with `original` rewritten to the real source line.
A salvaged diff is still `usable` only if the corrected text passes every other
check.

## Log

`--log` appends one JSON object per run:

```json
{"ts": "...", "resume_sha256": "...", "round": 2, "trigger": "eval:round1",
 "diffs": 3, "usable": 3, "blocked": {"missing": 0, "fabricated": 0, "noop": 0},
 "chain": {"prev_round": 1, "cites_prev": true}}
```

`chain.prev_round` is the last readable round already in the file;
`chain.cites_prev` is true when this run is the successor round and its trigger
names the round it is answering. Append-only: nothing here rewrites history, and
an agent that wants credit for iterating has to leave the trail.

## `apply.py`

Applies named diffs to a candidate copy, and re-runs the gate first. A diff that
is not `usable` in this run is refused even if it is listed in `--accept`, and a
salvaged diff is applied against the corrected source line. This exists so that
"I applied the accepted suggestions" cannot silently mean "I applied the blocked
ones too".

## Fixtures are the spec

`fixtures/` holds the golden scenarios in two language sets (`*.json` /
`*.en.json`), each with an `expected*.json` verdict table. `selftest.py` replays
them through the real code path and exits non-zero on any disagreement.

The [ResuAlign](https://github.com/shing26/ResuAlign-Lite) app vendors this file
and these fixtures, and its CI runs the same scenarios through its own engine
gate chain, asserting that both sides reach the same verdict. Consequences:

- a change to the verdict taxonomy, the summary line format, or the log schema is
  **breaking** and needs the fixtures plus the app-side copy moved together;
- loosening a rule is a product decision, not a refactor. If a rule is wrong,
  open an issue with the diff that got misjudged; the fix has to arrive as a new
  fixture scenario that both sides pass.

## Known limits of the check

- Content checks look at digits and Latin-script names. Free-form prose,
  including a coined Chinese technical phrase or an exaggerated verb, is only
  constrained by the verbatim-quote rule.
- Name detection in English treats a mid-sentence capitalized word as a name
  unless it is in a built-in list of ordinary capitalized words (months, weekdays,
  role nouns). Expect the occasional false block; the gate prefers that over an
  invented tool sailing through, and the reason line always names the token.
- The gate rules on provenance, not on relevance, quality, or match.
