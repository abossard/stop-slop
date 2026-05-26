# Stop Slop

A skill for removing AI tells from prose.

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
├── SKILL.md               # Core instructions (standalone use)
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
