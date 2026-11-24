# Stop Slop

A skill that makes an agent write text that a person can read at normal speed.

Frontier models write English that is correct and slow to read. They coin phrases, give things human verbs, stack nouns, drop "that", use nouns as verbs, and put a subject far from its verb. One 2026 study measured this across 14 models: Clark, Martin & Mahowald, [arXiv:2610.29162](https://arxiv.org/abs/2610.29162). The skill tells the agent to choose the few points that the reader needs and then to write each one out in full.

## How to use it

### GitHub Copilot CLI

```bash
copilot plugin install abossard/stop-slop
```

Then ask: `/stop-slop Rewrite README.md so that it reads more easily. Keep the facts.`

### Claude Code

```bash
claude plugin marketplace add abossard/stop-slop
claude plugin install stop-slop@stop-slop
```

Then ask: `/stop-slop:stop-slop Rewrite README.md so that it reads more easily. Keep the facts.`

For other agents, load [the skill](skills/stop-slop/SKILL.md) and keep its linked references accessible. Agents load it before they write text for a person.

## What is in it

- [The skill](skills/stop-slop/SKILL.md): the steps before and after writing, and the six constructions.
- [Constructions](references/constructions.md): each construction with examples from the study, a rewrite and the reading studies behind it.
- [Examples](references/examples.md): 28 texts from slop to no slop, from one sentence to a whole README. Each slop text is an original, word for word.
- [Research](references/research.md): what the study found, what it did not show, and where this repository departs from its method.

## Check a draft

From this checkout, with [uv](https://docs.astral.sh/uv/) installed:

```bash
tools/readcheck --file README.md
```

It prints one line per finding: the kind, the phrase, the fix and the sentence. `--json` adds the counts and the rates per 1,000 words. It also gives the average distance between words that belong together, corrected for sentence length.

The checker finds noun stacks, object relative clauses without "that", some human verbs on things, and subjects or objects that are far from their verb. It does not find coined phrases or nouns used as verbs. Its parser makes mistakes, so treat a finding as a question.

Without uv, the wrapper uses Python with spaCy and the `en_core_web_sm` model. It exits with code 3 when dependencies are missing.

## Does it work?

Not shown. The study measured what models write. It did not test whether an instruction such as this skill reduces the constructions, and this repository has not tested that either. `tools/readcheck` counts the constructions in a text, so you can compare a text written with the skill and a text written without it.

## Fork and license

Fork of [Hardik Pandya's stop-slop](https://github.com/hvpandya/stop-slop), maintained here by abossard.
[MIT license](LICENSE).
