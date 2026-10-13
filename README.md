# Stop Slop

## How to use it

### GitHub Copilot CLI

```bash
copilot plugin install abossard/stop-slop
```

Then ask: `/stop-slop Review README.md. Keep the facts; cut filler and repetition.`

### Claude Code

```bash
claude plugin marketplace add abossard/stop-slop
claude plugin install stop-slop@stop-slop
```

Then ask: `/stop-slop:stop-slop Review README.md. Keep the facts; cut filler and repetition.`

For other agents, load [the skill](skills/stop-slop/SKILL.md) and keep its linked references accessible.
Give it text or a file to review, or ask it to apply the guidance while drafting.

## Why use it

Use it when a reader has to work through filler to find the action, constraint, or reason.
The skill makes authors name who acts, state consequences, and keep each fact once.

Technical explanations should preserve why a choice exists. Link to code for recoverable details; keep necessary contracts and exceptions.
Tables and diagrams should clarify comparisons or relationships. Decorative visuals and repeated explanations make the reader do more work.

The skill reviews meaning and context. The analyzer flags sentences to inspect; its scores do not establish authorship or factual correctness.

## References

- [Writing rules](skills/stop-slop/SKILL.md): drafting and review.
- [Phrases](references/phrases.md): filler, vague claims, and plain-word swaps.
- [Structures](references/structures.md): repeated framing, hedges, and needed distinctions.
- [Visuals](references/visuals.md): choosing tables, diagrams, and prose.
- [Contrast research](references/contrastive-framing-research.md): legitimate contrasts versus redundant framing.
- [More examples](references/examples.md#real-beforeafter): edits from public repositories.

### Evidence

[Sources and evidence levels](references/evidence.md) distinguish research findings, practitioner guidance, and unverified rules.
The documentation rule follows [Ousterhout](https://web.stanford.edu/~ouster/cgi-bin/cs190-spring16/lecture.php?topic=comments) and [Nygard](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

## Details

### Standalone prose check

From this checkout, with [uv](https://docs.astral.sh/uv/) installed:

```bash
tools/slopometer --file README.md --json
```

The wrapper handles Python dependencies through uv. Without uv, it uses Python with the [required packages](tools/requirements.txt) and spaCy's `en_core_web_sm` model.
Missing dependencies stop the analyzer with exit code 3; it produces no report.

Review findings and compare revisions of the same text. A lower score alone does not show that an edit improved the writing.
Source-aware judgments, such as whether prose duplicates code or invents rationale, require review beyond the analyzer.

### Fork and license

Fork of [Hardik Pandya's stop-slop](https://github.com/hvpandya/stop-slop), maintained here by abossard.
This fork adds plugin packaging, a Python prose analyzer, research citations, and technical-writing and visual guidance.
[MIT license](LICENSE).

## Real examples

These are verbatim edits from public commit history.

| Edit | Before | After |
|------|--------|-------|
| Replace implementation history with the reader's action | The current pull request gives every child model one healthy dummy entity to confirm the deployment succeeded. The diagram labels that entity as a deployment check because it does not measure domain health. Replace it with the platform and system flows the domain provides. | Add monitoring signals to each child model before using its state to assess domain health. |
| Lead with the task | Trigger: the coherent task or session boundary has been reached with no active criteria and no blocking issue, or the user explicitly requested extract. It turns raw outcomes into durable knowledge under `raw/`, `wiki/`, and `schema.md`. | Turn this task's raw outcomes into durable knowledge under `raw/`, `wiki/`, and `schema.md`. Terminal phase, runs at most once. |

Sources: [Azure health-model documentation edit](https://github.com/Azure/azure-monitor-baseline-alerts/commit/23d41f17)
and [minime extract edit](https://github.com/abossard/virtucon/commit/725532b5).
