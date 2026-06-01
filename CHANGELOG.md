# Changelog

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
