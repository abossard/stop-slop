# Stop Slop

A skill for removing AI tells from prose.

> **Fork note — what this fork adds**
>
> The [original stop-slop](https://github.com/hvpandya/stop-slop) by [Hardik Pandya](https://hvpandya.com) is a pure-markdown skill that teaches LLMs to self-edit. This fork extends it with:
>
> - **Plugin support** — installable as a GitHub Copilot CLI or Claude Code plugin (`copilot plugin install`, `claude plugin add`)
> - **Empirically-backed vocabulary lists** — AI-overused words from [Kobak et al. (2025)](https://arxiv.org/abs/2406.07016) with frequency ratios (e.g. *delve* appears 28× more in AI text)
> - **Hedge stacking & symmetric list bloat** — two new structural patterns added to the detection rules
> - **Python analysis tool** (`tools/analyze.py`) — quantitative AI slop detection via burstiness scoring, lexical diversity (TTR, MTLD), AI vocabulary density, passive voice rate, and Flesch-Kincaid readability. Outputs per-sentence findings with actionable feedback. Works as a prose linter, not a classifier.
>
> The skill files and references remain backward-compatible with the original.

<img width="3840" height="2160" alt="G-Yg4RVbIAAhVxW" src="https://github.com/user-attachments/assets/902afc15-1f40-4a9d-af24-8cd67afb8ebf" />

## What this is

AI writing has patterns. Predictable phrases, structures, rhythms. This skill teaches Claude (or any LLM) to catch and remove them.

## Skill Structure

```
stop-slop/
├── .claude-plugin/
│   ├── plugin.json        # Plugin manifest
│   └── marketplace.json   # Marketplace manifest
├── skills/
│   └── stop-slop/
│       └── SKILL.md       # Skill for plugin discovery
├── tools/
│   ├── slopometer         # Wrapper: `uv run` preferred, `python3` fallback
│   ├── analyze.py         # AI slop analysis tool (Python, PEP 723)
│   ├── test_analyze.py    # Tests
│   └── requirements.txt   # Python deps (fallback path)
├── references/
│   ├── phrases.md         # Phrases to remove
│   ├── structures.md      # Structural patterns to avoid
│   └── examples.md        # Before/after transformations
├── README.md
└── LICENSE
```

## Install

### GitHub Copilot CLI

```bash
copilot plugin marketplace add abossard/stop-slop
copilot plugin install stop-slop@stop-slop
```

Verify:

```bash
copilot plugin list
```

### Claude Code

Add this folder as a skill, or install as a plugin:

```bash
claude plugin add abossard/stop-slop
```

### Other platforms

**Claude Projects:** Upload `SKILL.md` and reference files to project knowledge.

**Custom instructions:** Copy core rules from `SKILL.md`.

**API calls:** Include `SKILL.md` in your system prompt. Reference files load on demand.

## What it catches

**Banned phrases** - Throat-clearing openers, emphasis crutches, business jargon, all adverbs, vague declaratives, meta-commentary. See `references/phrases.md`.

**Structural clichés** - Binary contrasts, negative listings, dramatic fragmentation, rhetorical setups, false agency, narrator-from-a-distance voice, passive voice. See `references/structures.md`.

**Sentence-level rules** - No Wh- sentence starters, no em dashes, no staccato fragmentation, no lazy extremes, active voice required.

## Analysis Tool

A Python CLI for quantitative AI slop detection. Measures burstiness, lexical diversity, AI vocabulary density, passive voice rate, and readability — then flags specific sentences.

### Setup

The skill invokes the analyzer through `tools/slopometer`, which prefers [`uv`](https://docs.astral.sh/uv/) and requires no manual setup — PEP 723 inline metadata in `analyze.py` declares the deps, including the `en_core_web_sm` spaCy model.

```bash
brew install uv   # or: curl -LsSf https://astral.sh/uv/install.sh | sh
```

Fallback (no `uv`): the wrapper switches to `python3` and prints a one-line hint on stderr. To make the fallback work, install deps manually:

```bash
pip install -r tools/requirements.txt
python -m spacy download en_core_web_sm
```

### Usage

```bash
# Human-readable report from stdin
echo "your text here" | tools/slopometer

# JSON output for CI/scripting (parse with jq)
cat draft.md | tools/slopometer --json | jq '.findings'

# From file
tools/slopometer --file draft.md --json
```

The wrapper writes `runner=uv` or `runner=python3` to stderr so callers can verify which path executed.

### Metrics

| Metric | AI-like | Human-like | Source |
|--------|---------|------------|--------|
| Burstiness (sentence length variance) | < 0.3 | > 0.5 | GPTZero concept; multi_detector.py calibration |
| TTR (type-token ratio) | < 0.4 | > 0.5 | Opara 2024 (top-4 feature) |
| AI vocabulary density | > 10/1000 | < 5/1000 | Kobak et al. 2025 |
| Passive voice rate | > 20% | < 10% | Style guides |
| Hapax ratio (words appearing once / unique) | < 0.58 | > 0.60 | Opara 2024 (top-4); multi_detector.py |
| Yule's K (vocabulary repetition) | > 100 | < 100 | Retengart; multi_detector.py |
| Contraction rate (per sentence) | 0 | > 0 | Opara 2024 (formality signal) |

### Example output

```
═══ AI Slop Analysis ═══

Words: 42  |  Sentences: 4

Burstiness:          0.095 ⚠ AI-like (uniform sentence lengths)
TTR:                 0.738
AI vocab density:    238.1/1000 words ⚠ High AI vocabulary density
Passive voice rate:  25.0% ⚠ High passive voice rate
Flesch-Kincaid:      14.4
Hapax ratio:         0.812
Yule's K:            45.2
Contraction rate:    0.00/sentence (formal/AI-like)

── Findings (4 sentences flagged) ──

  [1] The landscape of modern technology has undergone a transformative shift.
      → AI-overused words: landscape, transformative (Kobak et al. frequency ratios)

  [2] Furthermore, the comprehensive ecosystem elucidates the interplay of factors.
      → AI-overused words: comprehensive, ecosystem, elucidates, interplay
      → AI-typical starter: "furthermore"
```

## Scoring

Rate 1-10 on each dimension:

| Dimension | Question |
|-----------|----------|
| Directness | Statements or announcements? |
| Rhythm | Varied or metronomic? |
| Trust | Respects reader intelligence? |
| Authenticity | Sounds human? |
| Density | Anything cuttable? |

Below 35/50: revise.

## Author

[Hardik Pandya](https://hvpandya.com)

## License

MIT. Use freely, share widely.
