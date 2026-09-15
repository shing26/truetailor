# Contributing

Three rules make this repo worth using, so they govern changes to it:

1. **`gate.py` stays one stdlib-only file.** No dependencies, no network, no
   config file. If a change needs any of those, it belongs in another project.
2. **Behavior lives in fixtures.** Any new rule, or any loosening of an existing
   one, arrives as a scenario in `fixtures/` plus the matching line in
   `expected*.json`, and `python selftest.py` must pass. A patch that edits the
   gate without touching the fixtures will be treated as suspicious, which is the
   intended culture here.
3. **Fail closed, and say why.** A block must name the number or term that has no
   source. If you cannot explain a block in one line, that is a bug in the detail
   text, not a reason to soften the verdict.

## Before opening a PR

```bash
python selftest.py
python gate.py --resume examples/demoflow/resume.md \
  --diffs examples/demoflow/diffs.round1.json \
  --allowlist examples/demoflow/gap.json
```

The second command should print 4 `OK`, 3 `BLOCK`, and one `GATE:` summary line.

## Reporting a misjudged diff

Paste the `GATE:` line and the diff that got ruled wrongly (JSON, with the
resume sentence it quotes). "It blocked my rewrite" is a signal the gate is
working; "it blocked a rewrite whose every word is in my resume" is a bug.

False blocks are recoverable: either the term belongs in the JD allowlist, or
the rewrite really did introduce a word the resume never had. False *passes* are
the ones that cost this project its reason to exist, so they get priority.
