# Changelog

## 2026-11-24

### Changed
- `SKILL.md` is rewritten around one study: Clark, Martin & Mahowald 2026, [arXiv:2610.29162](https://arxiv.org/abs/2610.29162). The author chooses the few points that the reader needs and writes each one in full. Six constructions get written out: coined phrases, human verbs on things, noun stacks, clauses without "that", nouns used as verbs, and subjects far from their verbs. The earlier rules on size, channel shapes and AI tells are gone from the skill.
- The README and the plugin descriptions describe the rewritten skill.
- The plugin version is 2.0.0-abossard.

### Added
- `references/constructions.md` gives each construction with examples quoted from the study, a rewrite and the reading studies behind it.
- `references/examples.md` keeps every slop text of the earlier file, word for word, and gives each one a new rewrite that follows the skill. It adds seven whole inputs of the removed evals, also word for word, with the text that the skill writes for each.
- `references/research.md` says what the study found, what it did not show, and where `readcheck` departs from its method.
- `tools/readcheck` finds noun stacks, object relative clauses without "that", a fixed list of human verbs on things, and subjects or objects 10 or more words from their verb. `--json` adds counts, rates per 1,000 words and the standardized dependency length.

### Removed
- `tools/analyze.py`, `tools/slopometer` and `tools/test_analyze.py`. They looked for AI tells, and the study does not link those to reading difficulty.
- The earlier references: `phrases.md`, `structures.md`, `visuals.md`, `review.md`, `evidence.md`, `contrastive-framing-research.md`, and the "after" texts and analyzer numbers of the earlier `examples.md`.
- `evals/`: the harness, its cases and its judge. Its checks tested length and format, and its judge's verdict changed with the reader that it stood in for.

### Not done
- Nobody has measured whether the skill reduces the constructions.

## 2026-10-24

### Changed
- `SKILL.md` works before drafting. The author takes the requested size literally, notes what the reader needs, picks a shape and ceiling per channel (chat, status, PR, commit, comment, email, code comment, doc note, ADR, plan) and reads the surrounding text before adding to a file. Drafting rules are fewer and positive; the tell list moved to the check after drafting.
- The description is quoted and asks agents to load the skill before writing anything a person will read. An unquoted ": " made the frontmatter invalid YAML, and Copilot then skipped the skill without an error.
- Deliverables never mention the skill, the analyzer, its metrics or scores. In 159 Copilot invocations, 51 listed the skills used and 34 pasted metrics into documents.
- The slopometer step is one command, `../../tools/slopometer --findings --file <path>`, and runs only for saved drafts over about 150 words. Agents had opened the analyzer source 61 times to learn its output and queried 54 times for JSON keys that do not exist.
- The Quick Checks, Wall of Shame and Scoring moved to `references/review.md` and apply only to review reports.

### Added
- `tools/analyze.py --findings` prints at most 10 findings, one per line, without metrics. The README documents the JSON keys.
- The analyzer flags a sentence-final ", not X" as `Contrast tail` and asks whether the reader might assume X. In 159 Copilot invocations, about 230 such tails appeared and 17 were flagged.
- `Bold label opener` flags "**Label:**" openers once two or more paragraphs or list items use them.
- `Repeats sentence N` flags a sentence that matches an earlier one word for word or nearly (word overlap of 0.8 or more, at least 6 words), compared with code and paths included.
- Requirement lines (EARS "shall" clauses, IDs such as `C1-5:`) get no findings, and headings keep only word-choice findings. On 60 real blueprints, long-sentence findings fell from 811 to 557 and passive-voice findings from 1,244 to 1,047.
- A paste-in writing contract for subagents that draft text, since they do not load the skill.
- `references/evidence.md` has a Prevention section: why models pad (length and typicality rewards), why few positive rules beat long ban lists, and why ceilings beat exact lengths.
- `evals/` runs the skill through GitHub Copilot CLI on 15 writing tasks built from the owner's real corrections. It grades deterministic checks, slopometer metrics and judge-model expectations, and compares versions blind against a reader profile.

## 2026-10-19

### Fixed
- `tools/analyze.py` runs on Python 3.13 and 3.14. Its inline metadata now asks for spaCy 3.8 and `en_core_web_sm` 3.8.0. The pinned 3.7.1 model held spaCy at 3.7.5, whose `blis` 0.7.11 fails to build on either version.
- `SKILL.md` gives the analyzer command as `../../tools/slopometer`, relative to the skill file like its reference links. An agent's shell starts in the user's project, where `tools/slopometer` does not exist.
- The Throat-Clearing Preamble table in `references/structures.md` shows its "Here's the thing:" row again. It had been joined to the row above.

## 2026-09-26

### Added
- `tools/analyze.py` flags sentences over 25 words, words with a plainer swap, stacked nominalizations and passives with no actor. It also flags an -ing clause that closes a sentence after a comma, and a subject 10 or more words from its verb. Defensive negation also catches completeness denials. New JSON keys report the counts: `long_sentence_count`, `plain_swap_count`, `nominalization_density`, `mean_dependency_distance`, `smog_index`, `dale_chall_score`, `difficult_word_rate`.
- Visual checks flag big Mermaid diagrams, long node labels, deep subgraphs, emoji used as decoration and steps written as a paragraph. `visual_findings` lists them with source line numbers, and `bold_density` counts prose bold without a finding.
- `references/visuals.md` says which content earns a diagram, table, list or prose, and lists the visual slop patterns.
- `references/phrases.md` adds a Plain Words table. Each row comes from the plainlanguage.gov list or the Plain English Campaign A to Z. A test keeps the table in sync with the analyzer.
- `references/structures.md` quotes the owner's real specimen of compliance narration and says what to write instead.
- `references/examples.md` adds seven real before/after pairs from the owner's commits in public repositories, each with slopometer numbers. A regression test checks that every BEFORE yields more issues than its AFTER.
- `skills/stop-slop/SKILL.md` adds four rules: length follows information, describe what the thing does, overview first, and plain words. It also adds quick checks for zombie nouns, -ing tails, subject-verb distance and visuals.
- The Wall of Shame gains a 🖼️ row, and Scoring gains a Visual fit row that passes at 42/60.
- The README Evidence section gives a source and an evidence level for each rule.

### Changed
- The sentence splitter ends a sentence at each markdown block boundary and skips fenced code. Headings, bullets and tables no longer merge into fake long sentences.
- A list item keeps its wrapped lines, and an ordered-list number never forms a sentence of its own.
- Inline code, link targets and bare URLs stay out of the word count and the sentence detectors. Link text still counts, and findings quote the sentence as written.
- spaCy parses each input once, and every detector reads its tokens from that parse by character offset.
- The adverb rule covers empty intensifiers and assertion adverbs, the two kinds the evidence supports cutting.
- The passive rule asks you to name the actor and allows passive when the thing acted on is the topic.
- `SKILL.md` frames sentence rhythm as an AI tell and asks for an average of 15 to 20 words, with a split past 25.
- Research citations moved from `SKILL.md` to the README, so the skill carries instructions only.
- The `SKILL.md` frontmatter triggers on requests to make text clearer and on diagram or table reviews.
- The README example output shows real output of the analyzer, with the command that produced it.
- The analyzer requires spaCy, `en_core_web_sm`, textstat and lexicalrichness. Without one of them it prints a banner on stderr and exits 3 instead of reporting degraded results. The `python3` wrapper hint names the four as required.

## 2026-08-11

### Added
- **Importance inflation via "decisive"** in `tools/analyze.py`: the verdict, role, turning-point and call-to-action frames listed in `references/phrases.md` are matched as collocations, not as a word, because the bare adjective is ordinary in military, sports and election prose. Ships with negative-control tests. `decisive`, `decisively` and `decisiveness` also join `AI_TIER2_WORDS`.
- **Defensive negation detector** in `tools/analyze.py`: flags a finished clause followed by a denial of a weaker claim nobody made (`asserts elapsed time, not merely that an error came back`; `the assertions are load-bearing, not decorative`). Separate from negative parallelism, which needs a `but`/`it's` alternative to complete the frame; here the denial stands alone. A sentence already reported as negative parallelism is skipped, so one negation frame yields one issue. That guard lives in `_generate_findings` control flow rather than a regex lookahead, because the sentence splitter leaves embedded periods (`v3.5`, `.But`) inside a sentence where a lookahead's `[^.!?]*` scan would stop early.
- `references/phrases.md`: **Technical-Register Slop** section covering importance labels (`load-bearing`, `decisive`, `the crux`, `not optional`), unimportance labels (`inert`, `no-op`, `cosmetic`, `harmless`, `dead code`), assertion adverbs (`exactly`, `actually`, `correctly`, `cleanly`), `silently` on its own, deliberateness signalling, self-praise adjectives, verdict openers, and sycophantic acknowledgements.
- `references/structures.md`: negation-as-proof, restatement escalation, em-dash bold clause, bold-label colon, parenthetical proof-stuffing, sentence bloat, self-interrogation, count-and-close, and justification tails.
- `references/examples.md`: nine before/after pairs (examples 6–14), each quoted verbatim from a single message in the source corpus.
- `skills/stop-slop/SKILL.md`: three core rules and eleven quick checks for the technical register.
- Regression tests for two failure modes found in review: a sentence matching both negation detectors is reported once, and pathological whitespace completes in under two seconds.

### Changed
- Frequency claims are measured over 1.82M words of assistant output (10,369 turns) and 1.02M words of blueprints (265 files), sentence-split with `_split_sentences` from `tools/analyze.py` at commit `b287cc1`: 87,261 and 48,739 sentences. Highest-volume tell is the em-dash bold clause at 15.2% of chat sentences.
- `not merely` / `not just` / `not only` added to the model-era signature marker table. It appears as a comma-framed tail at near-identical rates in both corpora (0.4% of blueprint sentences, 0.2% of chat), so the two are not compared.

### Fixed
- The second defensive-negation pattern wrote the optional article as `(?:a|an|the)?\s*` after `not\s+`, letting two quantifiers match the same run of spaces. That backtracked quadratically: 8.2s on 20,000 spaces. The article now owns its trailing whitespace, and the same input completes in 0.005s.

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
