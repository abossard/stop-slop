# Changelog

## 2026-08-11

### Added
- **Importance inflation via "decisive"** in `tools/analyze.py`: the verdict, role, turning-point and call-to-action frames listed in `references/phrases.md` are matched as collocations, not as a word, because the bare adjective is ordinary in military, sports and election prose. Ships with negative-control tests. `decisive`, `decisively` and `decisiveness` also join `AI_TIER2_WORDS`.
- `references/phrases.md`: "Importance Inflation: decisive" section with the frame list and rewrite guidance.

## 2026-08-10

### Added
- **Signature markers** in `tools/analyze.py`: occurrence-counted detection of model-era tics (`load-bearing`, `honest take`, `not nothing`, `sit with that`, `doing a lot of work`, `seam`). Counted by occurrence rather than density because the measured rate (19.5 hits/100k words on Opus 5) sits far below the 10/1000 density threshold.
- **Structural detectors**: negative parallelism (`it's not X, it's Y`), sycophantic openers (`You're absolutely right`), and throat-clearing metadiscourse (`Let me be honest`). Each ships with negative-control tests so ordinary negation and ordinary second-person sentences stay unflagged.
- **`syntactic_templates`** metric: POS n-gram template repetition for n in 4..8, following Shaib et al. 2024 (arXiv:2407.00211). Reported without a threshold, since the rate climbs with document length rather than measuring templating alone. `None` below 100 POS tokens or when spaCy is unavailable, with `syntactic_templates_unavailable_reason` distinguishing the two.
- **`kobak_common10_density`**, **`tier2_density`**, and **`em_dash_count`** metrics.
- `references/phrases.md`: model-era signature marker section.
- `references/structures.md`: sycophantic openers and throat-clearing preamble sections. Negative parallelism was already covered under "Binary Contrasts"; it is now machine-checked.

### Fixed
- `AI_TIER2_WORDS` and `KOBAK_COMMON_10` were defined but never read. Tier-2 words now raise an issue when clustered with another signal in the same sentence, and the common-10 set has its own density metric.
- Lexicon lookups no longer trust spaCy's lemma alone. In `The comprehensive review delves into crucial insights.`, spaCy tags `delves` as a noun and lemmatizes it to `delf`, silently dropping a tier-1 word. A lexicon miss now retries with suffix stripping.

### Changed
- Phrase matching uses one precompiled alternation instead of one regex scan per phrase. Equivalence verified across 3,000 randomized inputs. Per-call cost is unchanged within measurement noise; the change removes an O(phrases × text) scan that would have grown with the lexicon.

## 2026-06-01

### Added
- `tools/slopometer` wrapper script: prefers `uv run` (PEP 723 inline deps, zero-setup), falls back to `python3` with a stderr hint when `uv` is missing.
- PEP 723 inline-script metadata in `tools/analyze.py` so `uv run` resolves all deps (including the `en_core_web_sm` spaCy model wheel) on first invocation.
- Skill (`skills/stop-slop/SKILL.md`) now defines a **Quantitative check** step that invokes the wrapper before delivering prose.
- Parametrized `TestWrapper` cases covering `uv` and `python3-fallback` paths; `test_wrapper_no_runners_exits_nonzero` for the missing-runner contract.

### Changed
- README "Analysis Tool" section leads with `uv`; the manual `pip install` flow is documented as fallback.

## 2026-01-13

### Added

**Phrases (references/phrases.md)**
- Throat-clearing: "Here's what I find interesting", "Here's the problem though"
- Performative emphasis: "creeps in", "I promise", "They exist, I promise"
- Telling instead of showing: "This is genuinely hard", "This is what leadership actually looks like"

**Structures (references/structures.md)**
- Binary contrasts: "Not X. But Y.", "It's not this. It's that.", "stops being X and starts being Y"
- Rhythm patterns: staccato fragmentation, dashes for dramatic pause, hedging as reassurance
- Word patterns: absolute words (always, never, everyone, etc.), AI-overused intensifiers (deeply, truly, fundamentally, inherently, simply, literally, inevitably)

## 2026-01-12

- Restructured skill following Claude Code best practices (PR #1)
- Split into SKILL.md and references/ folder

## 2025-01-12

- Initial release
