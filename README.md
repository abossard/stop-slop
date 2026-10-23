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
Agents load it before they write text for a person, such as a PR description, comment, email, doc or explanation, and when you ask for a review.

## Why use it

Use it when a reader has to work through filler to find the action, constraint, or reason.
Readers judge slop mostly by missing or irrelevant information, not by word choice, so the skill starts before the first sentence.
The author takes the requested size literally, notes what the reader needs, picks the shape for the channel and sets a ceiling.
While drafting, the author names who acts, states consequences, claims only what was checked and keeps each fact once.
Phrase lists and the analyzer check the draft afterwards.

Technical explanations should preserve why a choice exists. Link to code for recoverable details; keep necessary contracts and exceptions.
Tables and diagrams should clarify comparisons or relationships. Decorative visuals and repeated explanations make the reader do more work.

The skill reviews meaning and context. The analyzer flags sentences to inspect; its scores do not establish authorship or factual correctness.

## References

- [Writing rules](skills/stop-slop/SKILL.md): drafting, checking and review.
- [Review](references/review.md): checklist, Wall of Shame and scores for review reports.
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
tools/slopometer --file README.md --findings
```

`--findings` prints at most 10 findings, one per line: `S3` is the third prose sentence, `L12` is source line 12 for a visual finding. `--json` prints every metric and finding: each entry in `findings[]` has `line` (the sentence number), `sentence` (an excerpt) and `issues[]`, and each entry in `visual_findings[]` has `line` (the source line), `kind` and `issue`.
Requirement lines (EARS "shall" clauses, IDs such as `C1-5:`) get no findings, and headings get only word-choice findings.

The wrapper handles Python dependencies through uv. Without uv, it uses Python with the [required packages](tools/requirements.txt) and spaCy's `en_core_web_sm` model.
Missing dependencies stop the analyzer with exit code 3; it produces no report.

Review findings and compare revisions of the same text. A lower score alone does not show that an edit improved the writing.
Source-aware judgments, such as whether prose duplicates code or invents rationale, require review beyond the analyzer.

### Evals

[evals/](evals/README.md) runs the skill through GitHub Copilot CLI on 15 writing tasks taken from real corrections, grades the results and compares skill versions blind.

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
