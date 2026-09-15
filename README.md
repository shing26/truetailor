# true-tailor

**A resume tailoring skill where the fabrication gate is code, not a promise.**

Every "tailor my resume to this JD" tool is a prompt. Ask it not to invent and
it promises it won't, then happily writes "streamed through Kafka" because Kafka
is a word that fits the sentence. `true-tailor` is a two-file skill for
agents (Claude Code, Codex): the skill file makes the model produce diff-shaped
suggestions with verbatim quotes, and `gate.py` - one 500-line Python standard
library file, no install, no network, no API key - rejects any suggestion whose
numbers, named tools, or source quote cannot be found in the candidate's own
resume. The model does not get a vote on that step.

```
BLOCK demo-d4-fabricated-throughput [add/fabricated] number 12000 has no source in the resume
BLOCK demo-d5-fabricated-stack [modify/fabricated] term Kafka has no source in the resume
```

60 seconds of it happening, on a synthetic resume and a synthetic JD:
[docs/gate-demo.mp4](docs/gate-demo.mp4). The clip is a terminal replay of the
checked-in [examples/demoflow](examples/demoflow) run, not a staged mock: every
line in it came out of the commands printed in this README.

## Try the gate in 30 seconds, without a model

The gate is deterministic, so you can watch it work before you trust a single
word of this README:

```bash
git clone https://github.com/shing26/truetailor
cd truetailor
python selftest.py          # any python3, stdlib only
```

It replays 17 golden scenarios (Chinese and English resumes) through the same
`gate.py` your agent would call, and prints how each was ruled:

```
english fixtures
  ok   e1-clean-modify                  usable/verified
  ok   e2-midsentence-tool-invented     blocked/fabricated - term Kafka has no source in the resume
  ok   e3-midsentence-employer-invented blocked/fabricated - term Baseten has no source in the resume
  ok   e4-sentence-start-is-prose       usable/verified
  ok   e5-capitalized-common-word       usable/verified
  ok   e6-allowlist-term                usable/verified
  ok   e7-misquoted-salvage             usable/verified (quote salvaged)
  GATE: 7 diffs / 2 blocked (missing=0, fabricated=2, noop=0) / resume-sha256=ad81c9508195
  ok   e6-allowlist-term                blocked without the allowlist, as designed
```

Four of those seventeen encode bugs the parent app really shipped and had to fix:
an unsourced metric, a no-op "suggestion", and two `add` diffs that skipped the
content check entirely. The rest are planted to prove each class of lie gets
caught. The fixture files are the spec: `fixtures/expected*.json` says what the
gate must do, `selftest.py` fails if it stops doing it.

## Install

```bash
# Claude Code
git clone https://github.com/shing26/truetailor ~/.claude/skills/true-tailor

# Codex
git clone https://github.com/shing26/truetailor ~/.codex/skills/true-tailor
```

Windows:

```powershell
git clone https://github.com/shing26/truetailor $env:USERPROFILE\.claude\skills\true-tailor
```

Then, in a checkout of your own work:

> Tailor my resume to this JD. `resume.md` is my master resume, the JD is below.

Paste both as text. The skill takes it from there and you will see the `GATE:`
line it had to paste.

## The loop

| Step | Who does it | Output |
|---|---|---|
| 0. Inputs | you | `resume.md`, `jd.txt` |
| 1. Gap analysis | model | `gap.json` - what the JD buys, what the resume proves but never says, what cannot honestly be tailored |
| 2. Rewrite diffs | model | `diffs.json`, each carrying a verbatim quote of the line it rests on |
| 3. Gate | **`gate.py`** | one verdict per diff + one `GATE:` summary line, pasted verbatim into the reply |
| 4. Apply + re-evaluate | `apply.py` + model | candidate copy, `EVAL round N:`, and a next round that must cite it |

Step 3 is not optional and the model is not the judge. `apply.py` re-runs the
gate before writing anything, so a blocked diff cannot quietly become a line in
your resume:

```
applied demo-d1-service-ownership
applied demo-d3-runbooks-salvaged (salvaged quote)
refused demo-d4-fabricated-throughput: not gate-cleared this run
4/5 accepted diffs -> examples/demoflow/resume.r1.md
```

A run you can reproduce end to end, on invented people, is checked in:
[examples/demoflow/](examples/demoflow). Two rounds, two planted fabrications,
one planted no-op, one salvage, and a `tailoring.jsonl` that proves the second
round followed the first.

## What the gate enforces

Checked on every diff, in every round, by code:

- **provenance is locatable** - the quote must be found in the resume. Verbatim,
  or whitespace/misquote tolerant, in which case the diff is marked `salvaged`
  and the quote gets rewritten to the real source line, so nobody can cite a
  sentence that does not exist;
- **numbers have a source** - every digit in the rewrite must already appear in
  the resume, the anchor sentence, or the JD allowlist;
- **names have a source** - acronyms, mixed-case tools (`FastAPI`, `PyTorch`),
  and mid-sentence capitalized proper nouns (`Kafka`, `Baseten`) must appear in
  one of those too. Sentence-initial capitalization and ordinary capitalized
  words do not count as names, so prose rewrites are not shredded;
- **an `add` must carry its supporting sentence**, and a rewrite that changes
  nothing is blocked as `noop` rather than counted as a suggestion.

## What the gate does not do

The list matters more than the feature list, because a tool that overstates this
is worse than no tool:

- It cannot catch an invented claim written in Chinese, or in lowercase English.
  Chinese has no word boundaries to check, so Chinese text is constrained by the
  verbatim-quote rule instead - and inside Chinese text every Latin word is
  treated as a term, which is stricter than the English path.
- It does not know whether a rewrite is *worth making*. Match quality is Step 1
  and Step 4 judgment, done by a model, labeled as such.
- It is not a lie detector about emphasis. Turning "participated in" into
  "owned" needs a human, and the resume owner is the human.
- Zero usable diffs is a legitimate outcome. The skill is required to report it
  as one - with an explicit distinction between "this round produced nothing"
  and "there was nothing to fix" - instead of dressing up an empty run.

## The audit trail

`--log tailoring.jsonl` appends one line per gated run:

```json
{"round": 2, "trigger": "eval:round1", "diffs": 3, "usable": 3,
 "blocked": {"missing": 0, "fabricated": 0, "noop": 0},
 "resume_sha256": "969f7162d0e0...", "chain": {"prev_round": 1, "cites_prev": true}}
```

`chain` is the part that makes "we iterated on this resume" checkable: a round
must follow the previously logged round and cite it. The resume hash changes
between rounds, so a re-run of the same text cannot be presented as progress.
If you ever want to show someone proof, show this file and the `GATE:` lines,
not the chat summary.

## Contract

`docs/gate-contract.md` fixes the input/output shape: `resume.md + diffs.json
(+ allowlist)` to per-diff verdicts, one machine-readable summary line, append
only JSONL. The app this came from (
[ResuAlign](https://github.com/shing26/ResuAlign-Lite)) vendors `gate.py`
byte-identically and runs the same fixtures through its own engine chain, so
neither side can drift into being more permissive than the other.

## Why a skill and not an app

The valuable part of resume tailoring is not the UI. It is a rule that holds
when nobody is watching. A markdown file plus one stdlib script can carry that
rule into whatever tool you already use, with your own model and no account.
This repo is deliberately small: `SKILL.md`, `gate.py`, `apply.py`,
`selftest.py`, fixtures, examples. If you want persistent version history,
multi-role batches, or a review board for the diffs, that is what the app is
for - but the 30-second version lives here.

## Feedback

Open a [discussion](https://github.com/shing26/truetailor/discussions) with the
format "I expected X and saw Y", plus the `GATE:` line from your run. First-run
friction is the whole point of this project, so a confused agent is a bug report
even when the gate behaved correctly.

MIT - see [LICENSE](LICENSE).
