---
name: stop-slop
description: Remove AI writing patterns from prose. Use when drafting, editing, or reviewing text to eliminate predictable AI tells.
when_to_use: "When writing, editing, or reviewing prose and you want to catch and remove predictable AI writing patterns like filler phrases, structural clichés, and rhythm issues."
---

# Stop Slop

Eliminate predictable AI writing patterns from prose.

## Core Rules

1. **Cut filler phrases.** Remove throat-clearing openers, emphasis crutches, and all adverbs. See [references/phrases.md](../../references/phrases.md).

2. **Break formulaic structures.** Avoid binary contrasts, negative listings, dramatic fragmentation, rhetorical setups, false agency. See [references/structures.md](../../references/structures.md).

3. **Use active voice.** Every sentence needs a human subject doing something. No passive constructions. No inanimate objects performing human actions ("the complaint becomes a fix").

4. **Be specific.** No vague declaratives ("The reasons are structural"). Name the specific thing. No lazy extremes ("every," "always," "never") doing vague work.

5. **Put the reader in the room.** No narrator-from-a-distance voice. "You" beats "People." Specifics beat abstractions.

6. **Vary rhythm.** Mix sentence lengths. Two items beat three. End paragraphs differently. No em dashes.

7. **Trust readers.** State facts directly. Skip softening, justification, hand-holding.

8. **Cut quotables.** If it sounds like a pull-quote, rewrite it.

## Quick Checks

Before delivering prose:

- Any adverbs? Kill them.
- Any passive voice? Find the actor, make them the subject.
- Inanimate thing doing a human verb ("the decision emerges")? Name the person.
- Sentence starts with a Wh- word? Restructure it.
- Any "here's what/this/that" throat-clearing? Cut to the point.
- Any "not X, it's Y" contrasts? State Y directly.
- Three consecutive sentences match length? Break one.
- Paragraph ends with punchy one-liner? Vary it.
- Em-dash anywhere? Remove it.
- Vague declarative ("The implications are significant")? Name the specific implication.
- Narrator-from-a-distance ("Nobody designed this")? Put the reader in the scene.
- Meta-joiners ("The rest of this essay...")? Delete. Let the essay move.

## 🏆 Wall of Shame

When reviewing or diagnosing prose, surface the most ridiculous AI slop you found. Pick up to 3 worst offenders — real sentences from the text. Skip this section if the text has no clear offenders. Do not invent examples.

For each offender, tag it with one emoji and a one-line roast. Roast the sentence, not the writer.

| Emoji | Offense |
|-------|---------|
| 🤖 | Robotic phrasing — sounds like a chatbot wrote it |
| 💀 | Dead cliché — "It's important to note," "In today's world" |
| 🎭 | Fake drama — manufactured urgency or gravity |
| 🪞 | Self-referential — the text talks about itself |
| 🫠 | Cringe filler — adds nothing, sounds desperate to fill space |
| 🦜 | Parrot — repeats the same idea in slightly different words |

**Format:**

> 🤖 "This comprehensive guide provides a detailed overview of the key considerations."
> → It's a list, not a comprehensive guide. Say what it covers.
>
> 💀 "It's important to note that security plays a crucial role."
> → Everything in a security doc is important to note. Cut the throat-clearing.
>
> 🎭 "In an era of unprecedented digital transformation, organizations must navigate..."
> → Nobody talks like this. Say what changed and what to do about it.

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

## Examples

See [references/examples.md](../../references/examples.md) for before/after transformations.

## Research References

Signals and thresholds in this skill are backed by peer-reviewed and practitioner research:

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

Key findings:
- **Top 4 discriminating features** (Opara 2024): UniqueWordCount, StopWordCount, TTR, HapaxLegomenonRate
- **Kobak "common 10" words** whose aggregate frequency predicts LLM use: across, additionally, comprehensive, crucial, enhancing, exhibited, insights, notably, particularly, within
- **LLM text has collapsed entropy** (Mahapatra 2026): 1,949–16,853% amplification of certain patterns, complex punctuation suppressed to 3.2–23.2% of baseline

## License

MIT
