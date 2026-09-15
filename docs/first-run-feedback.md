# First-run feedback protocol

This repo is one markdown file plus one verifier. The interesting failure mode
is not the gate misbehaving - it is an agent reading `SKILL.md` differently than
the author does. The author's own runs prove very little, so first runs from
anyone else are the entire signal.

Run it once on your own resume and one real JD, then post in
[the pinned discussion](https://github.com/shing26/truetailor/discussions) in
this shape:

```
I expected: <what you thought would happen>
I saw:      <what actually happened>
Host:       Claude Code / Codex, which model, which OS
GATE:       <paste the summary line verbatim>
```

The `GATE:` line matters more than the prose: it is the part that cannot be
embellished. If you would rather not paste it, paste nothing and say why -
"it stalled at step 2" is still a usable report.

## What happens to each report

- friction in a first run gets fixed in `SKILL.md`, not excused;
- a diff the gate misjudged becomes a scenario in `fixtures/`, in whichever
  direction it failed: a false block and a false pass are both bugs, and rules
  without a failing test are vibes;
- if the conclusion is that this is not worth using, that is also a result, and
  it gets stated here rather than quietly abandoned.

## Two limits worth knowing before you spend your first run

- Weak local models produce thin rounds. The gate reports that honestly
  (`usable=0` is a result to state, not a status to hide), but it cannot make
  the suggestions good.
- The gate rules on provenance, not on whether a rewrite is worth making.
  "What the gate does not do" in the README is the full list.
