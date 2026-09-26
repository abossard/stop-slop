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
> - **Clarity and visual checks.** Flags long sentences, plain-word swaps, zombie nouns, passives with no actor, -ing tails and distant verbs. Checks Mermaid size, decorative emoji and steps written as prose. [Evidence](#evidence) lists a source for each new rule.
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
│   ├── visuals.md         # When to use a visual, and visual slop
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

**Banned phrases** - Throat-clearing openers, emphasis crutches, business jargon, empty intensifiers and adverbs that claim a check, vague declaratives, meta-commentary, words with a plainer swap. See `references/phrases.md`.

**Structural clichés** - Binary contrasts, negative listings, dramatic fragmentation, rhetorical setups, false agency, narrator-from-a-distance voice, passive voice with no actor, compliance narration. See `references/structures.md`.

**Sentence-level rules** - No Wh- sentence starters, no em dashes, no staccato fragmentation, no lazy extremes, no sentences over 25 words, a named actor.

**Visuals** - Diagrams that restate the prose, oversized Mermaid diagrams, emoji as decoration, steps written as a paragraph. The skill tags decorative visuals 🖼️ in its Wall of Shame. See `references/visuals.md`.

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

The analyzer requires spaCy, `en_core_web_sm`, textstat and lexicalrichness. Without any of them it prints a banner naming each missing one and its fix, then exits 3 with nothing on stdout.

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
| Signature markers (raw count) | any occurrence | 0 | claude-code#53454 frequency data |
| Kobak common-10 density | > 20/1000 | < 20/1000 | Kobak et al. 2025 (Δcommon=0.134) |
| Template rate (repeated POS n-grams) | n/a | n/a | Shaib et al. 2024, arXiv:2407.00211 |
| Tier-2 density | context-dependent | n/a | flagged only when clustered |
| Em dash count | n/a | n/a | house style (`references/structures.md`) |
| Long sentences (`long_sentence_count`, over 25 words) | n/a | n/a | GOV.UK style guide |
| Plain-word swaps (`plain_swap_count`) | n/a | n/a | plainlanguage.gov; Plain English Campaign |
| Nominalization density (`nominalization_density`, per 1000 words) | higher | lower | Coleman 1964; Reinhart et al. 2025 |
| Mean dependency distance (`mean_dependency_distance`) | longer | shorter | Gibson 1998; Muñoz-Ortiz et al. 2024 |
| SMOG (`smog_index`) | n/a | n/a | McLaughlin 1969 via textstat |
| Dale-Chall (`dale_chall_score`) | n/a | n/a | Dale & Chall 1948 via textstat |
| Difficult-word rate (`difficult_word_rate`, proper nouns excluded) | n/a | n/a | Dale-Chall word list via textstat |
| Bold density (`bold_density`, bold spans per 100 prose words) | n/a | n/a | Wikipedia "Signs of AI writing"; reported without a finding |
| Visual findings (`visual_findings`, list of `{line, kind, issue}`) | any entry | empty | `references/visuals.md` |

Markdown headings, list items, table rows and blockquote lines each end a sentence; a list item keeps its wrapped lines. Table rows, fenced code, inline code, link targets and bare URLs stay out of the sentence and word counts.

The Mermaid checks use a line-based regex, since Python has no Mermaid parser. They read the flowchart node shapes, bare IDs and edge labels. One-line `graph TD; A-->B` diagrams, `~~~` links, numeric IDs and v11 `@{ shape }` nodes go uncounted.

Readability formulas explain roughly a quarter to a third of reader difficulty ([Crossley et al. 2023](https://doi.org/10.3758/s13428-022-01802-x)). Use them to compare drafts of one text.

`template_rate` is reported without a threshold. It is **not length-invariant**:
on one human-written corpus it measured 0.13 at 150 words and 0.61 at 28,000
words, because longer texts give every POS n-gram more chances to recur. Compare
it only between texts of similar length. `pos_token_count` is reported alongside
it so you can tell whether two numbers are comparable.

### Signature markers

Some tells are too rare for a density metric to catch. Anthropic's own issue
tracker measured `load-bearing` at **19.5 hits per 100k words** on Opus 5,
roughly 0.2 per 1000 words, when the AI-vocabulary flag needs 10 per 1000. The
same data shows it is a version regression, not a constant: 0.5 per 525
messages on Opus 4.6 against 12.0 on Opus 4.7.

So these markers are counted by occurrence and reported whenever they appear:
`load-bearing`, `honest take`, `not nothing`, `sit with that`,
`doing a lot of work`, `seam`.

The tool also flags three structural tells behind them: negation-then-correction
frames (`it's not X, it's Y`), sycophantic openers (`You're absolutely right`),
and throat-clearing preambles (`Let me be honest`).

Sources: [claude-code#53454](https://github.com/anthropics/claude-code/issues/53454),
[r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/comments/1tob6q5/that_is_loadbearing/),
[jola.dev](https://jola.dev/posts/how-to-stop-claude-from-saying-load-bearing),
[Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing).

### Why LLM prose reads this way

Three separate causes, not one:

- **Reward models track length.** A purely length-based reward reproduces most downstream RLHF gains ([arXiv:2310.03716](https://arxiv.org/abs/2310.03716)), which favours preamble and caveats over direct answers.
- **RLHF collapses diversity.** It "significantly reduces output diversity compared to SFT" ([arXiv:2310.06452](https://arxiv.org/abs/2310.06452)).
- **Templates predate alignment.** 76% of templates in model output trace back to pretraining data and "are not overwritten during fine-tuning or alignment processes such as RLHF" ([arXiv:2407.00211](https://arxiv.org/abs/2407.00211)).

Sycophantic openers are a measured artifact too: preference models favour responses matching the user's view ([arXiv:2310.13548](https://arxiv.org/abs/2310.13548)).

### Example output

```bash
printf '%s\n' "The landscape of modern technology has undergone a transformative shift." \
  "Furthermore, the comprehensive ecosystem elucidates the interplay of factors." | tools/slopometer
```

```
═══ AI Slop Analysis ═══

Words: 19  |  Sentences: 2

Burstiness:          0.074
TTR:                 0.842
AI vocab density:    315.8/1000 words ⚠ High AI vocabulary density
Passive voice rate:  0.0%
Flesch-Kincaid:      14.2
SMOG:                14.6
Dale-Chall:          14.1
Difficult words:     57.9%
Readability formulas explain roughly a quarter to a third of reader difficulty.
Contraction rate:    0.00/sentence
Tier-2 density:      52.6/1000 words (flagged only in clusters)
Kobak common-10:     52.6/1000 words ⚠ Kobak common-10 cluster
Em dashes:           0

Sentence lengths: mean=9.5, stdev=0.7, min=9, max=10

── Findings (2 sentences flagged) ──

  [1] The landscape of modern technology has undergone a transformative shift.
      → AI-overused words: landscape, transformative (Kobak et al. frequency ratios)

  [2] Furthermore, the comprehensive ecosystem elucidates the interplay of factors.
      → AI-overused words: furthermore, ecosystem, elucidates, interplay (Kobak et al. frequency ratios)
      → AI-typical starter: "furthermore"
      → Tier-2 AI words clustered with other signals: comprehensive
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
| Visual fit | Does each visual add information the prose lacks? |

Below 42/60: revise.

## Evidence

These sources back the analyzer signals and the clarity and visual rules. Strong means replicated, a meta-analysis, a large corpus or an official standard. Moderate means one good study. Practitioner means style guides, agent skills or lab policy.

### AI-writing signals

| Source | Signal | Citation |
|--------|--------|----------|
| Kobak et al. (2025) | AI vocabulary excess words, frequency ratios | *Science Advances* Vol.11 No.27; arXiv:2406.07016 |
| Opara (StyloAI, 2024) | TTR, hapax legomena ratio as top-4 features; contraction count | AIED 2024; arXiv:2405.10129 |
| Mahapatra (2026) | Language entropy collapse, punctuation suppression, distinct-N | arXiv:2605.28826 |
| Przystalski et al. (2025) | Stylometric features on short texts (10 sentences), grammatical standardization | *Expert Systems with Applications* 296; arXiv:2507.00838 |
| Ochab et al. (StylOch, 2025) | POS n-gram frequencies, dependency parse features | arXiv:2507.12064 |
| Aityan et al. (NEULIF, 2025) | Stylometric + readability features achieve 97% accuracy with 25MB CNN | arXiv:2511.21744 |
| chepdor2-ai/humara-s-clean-canvas | Calibrated thresholds for burstiness, Yule's K, hapax ratio, Guiraud's R | github.com/chepdor2-ai/humara-s-clean-canvas |
| Retengart/entropy-analysis | Yule's K, MTLD, burstiness B-index formulas | github.com/Retengart/entropy-analysis |
| Reinhart et al. (2025) | Present participle clauses, nominalizations and passive voice separate LLM from human text | *PNAS* 122, e2422455122; arXiv:2410.16107 |
| Muñoz-Ortiz et al. (2024) | LLM news text has longer dependency distances | *Artificial Intelligence Review* 57, 265; arXiv:2308.09067 |
| Geng & Trotta (2025) | Word lists decay: "delve" fell after its overuse was publicized | ACL Findings 2025; arXiv:2502.09606 |

Key findings:
- **Top 4 discriminating features** (Opara 2024): UniqueWordCount, StopWordCount, TTR, HapaxLegomenonRate
- **Kobak "common 10" words** whose aggregate frequency predicts LLM use: across, additionally, comprehensive, crucial, enhancing, exhibited, insights, notably, particularly, within
- **LLM text has collapsed entropy** (Mahapatra 2026): 1,949–16,853% amplification of certain patterns, complex punctuation suppressed to 3.2–23.2% of baseline

### Clarity

| Rule | Finding | Level | Source |
|------|---------|-------|--------|
| Average 15 to 20 words, split past 25 | Shorter average sentences improve comprehension; guides converge on 15 to 25 words | strong | Cook et al. 2023, [PLOS ONE](https://doi.org/10.1371/journal.pone.0282146); [GOV.UK style guide](https://www.gov.uk/guidance/style-guide); EU DGT Clear Writing; [Plain English Campaign](https://www.plainenglish.co.uk) |
| Rhythm as an AI tell only | No study shows that varied sentence length helps readers | unverified | Meister et al. 2021, [EMNLP](https://doi.org/10.18653/v1/2021.emnlp-main.74), has no sentence-length claim |
| Name the actor, passive when the object is the topic | Passive is slower on average and faster when the object is the topic | strong | Slobin 1966, [doi](https://doi.org/10.1016/S0022-5371(66)80023-3); Olson & Filby 1972, [doi](https://doi.org/10.1016/0010-0285(72)90013-8) |
| Zombie nouns | Nominalized sentences are harder to understand | strong | Coleman 1964, [doi](https://doi.org/10.1037/h0040440) |
| Negation tails | Negation adds a processing step | strong | Clark & Chase 1972, [doi](https://doi.org/10.1016/0010-0285(72)90019-9); Kaup et al. 2006, [doi](https://doi.org/10.1016/j.pragma.2005.09.012) |
| Subject-verb distance | Longer distance makes integration harder | strong | Gibson 1998, [doi](https://doi.org/10.1016/S0010-0277(98)00034-1); Grodner & Gibson 2005, *Cognitive Science* 29(2) |
| Plain words | Needlessly complex words lower judged author intelligence | strong | Oppenheimer 2006, [doi](https://doi.org/10.1002/acp.1178); swap list from [plainlanguage.gov Simple Words and Phrases](https://web.archive.org/web/20161223073724/http://www.plainlanguage.gov/howto/wordsuggestions/simplewords.cfm) and the [Plain English Campaign A to Z](https://web.archive.org/web/20200109034429/http://www.plainenglish.co.uk/files/alternative.pdf) |
| Adverbs: empty intensifiers and assertion adverbs only | No evidence against adverbs as a class; filler hedges cost credibility | weak | Hosman 1989, [doi](https://doi.org/10.1111/j.1468-2958.1989.tb00190.x); Durik et al. 2008, [doi](https://doi.org/10.1177/0261927X08317947) |
| Readability formulas as a comparison | FKGL R² 0.27, SMOG 0.32, Dale-Chall 0.31 on 4,724 texts | strong | Crossley et al. 2023, [doi](https://doi.org/10.3758/s13428-022-01802-x) |
| Readability formulas as a comparison | About half of 36 studies improved comprehension by chasing the score | strong | Klare 1976 via Redish 2000, *ACM J. Computer Documentation* 24(1) |
| Length follows information | Concise text scored 58% better on usability; concise, scannable and objective text scored 124% better | strong | [Morkes & Nielsen 1997](https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/) |
| Overview first, details after | Headings and previews improve memory for the content they cue | moderate | Lorch 1989, [doi](https://doi.org/10.1007/BF01320135) |
| Dropped: "8 words = 100% comprehension" | No primary source; absent from Gunning 1952 and American Press Institute archives | folklore | none found |

### Visuals

| Rule | Finding | Level | Source |
|------|---------|-------|--------|
| Diagram for linked steps and relations | Diagrams group related information by location and cut search | strong | Larkin & Simon 1987, [doi](https://doi.org/10.1111/j.1551-6708.1987.tb00863.x) |
| Arrows for sequence and causality | Arrows encode direction, time and cause | moderate | Tversky et al. 2000, [doi](https://doi.org/10.1007/3-540-44590-0_21) |
| Table for lookup, chart for trends | Tables fit point lookup; charts fit trends | strong | Vessey 1991, [doi](https://doi.org/10.1111/j.1540-5915.1991.tb00344.x); Cleveland & McGill 1984, *JASA* 79(387) |
| Tree or nested list for hierarchy; overview first | Tree and network data need their own overview and drill-down | strong | Shneiderman 1996, [doi](https://doi.org/10.1109/VL.1996.545307) |
| A visual must add information | A redundant second source hurts learning; decorative pictures add nothing | strong | Sweller et al. 2019, [doi](https://doi.org/10.1007/s10648-019-09465-5), Table 1; Carney & Levin 2002, [doi](https://doi.org/10.1023/A:1013176309260) |
| Headings as signals | Signaling helps a little, r = 0.17 over 27 studies | strong | Richter et al. 2016, [doi](https://doi.org/10.1016/j.edurev.2015.12.003) |
| Split Mermaid past 20 nodes | Above about 20 nodes, matrices beat node-link diagrams on most tasks | strong | Ghoniem et al. 2004, [doi](https://doi.org/10.1109/INFVIS.2004.1) |
| Few edge crossings | Edge crossings hurt graph reading most | moderate | Purchase 1997, [doi](https://doi.org/10.1007/3-540-63938-1_67) |
| Subgraph depth 2 | Working memory holds about 4 chunks | strong, applied by inference | Cowan 2001, [doi](https://doi.org/10.1017/S0140525X01003922) |
| Labels up to about 5 words, flag past 7 | Agent skills converge on 5 words per label | practitioner | [bentossell/visualise](https://github.com/bentossell/visualise) |
| Single fact as a sentence | A list or table needs more than one item | practitioner | [Microsoft Writing Style Guide](https://learn.microsoft.com/style-guide/scannable-content/lists) |
| Emoji and bold as AI tells | Named tells; Anthropic's system prompt avoids both by default | practitioner, lab policy | [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing); [Claude system prompts](https://platform.claude.com/docs/en/release-notes/system-prompts) |
| Why models over-format | Arena votes reward length and markdown; the same model scored 18.3 points apart by style alone | strong | [LMSYS style control 2024](https://lmsys.org/blog/2024-08-28-style-control/); arXiv:2406.11939 |
| Dropped: ADHD readers prefer visuals | No study found; learning-style matching is a known neuromyth | unverified | [Frontiers in Education 2023 review](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2023.1147498/full) |

The analyzer uses only textstat, spaCy and lexicalrichness. wordfreq is frozen by its maintainer, LFTK carries a non-commercial license, and proselint needs Python 3.10.

## Author

[Hardik Pandya](https://hvpandya.com)

## License

MIT. Use freely, share widely.
