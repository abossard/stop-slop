---
name: stop-slop
description: Remove AI tells and unclear writing. Use when you write or review text, make text clearer, or review a diagram or table.
when_to_use: "When prose has filler, clichés or rhythm issues, when text should be clearer, or when a diagram or table needs review."
---

# Stop Slop

Eliminate predictable AI writing patterns from prose.

## Core Rules

1. **Cut filler phrases.** Remove throat-clearing openers, emphasis crutches, empty intensifiers and assertion adverbs. See [references/phrases.md](../../references/phrases.md).

2. **Break formulaic structures.** Avoid binary contrasts, negative listings, dramatic fragmentation, rhetorical setups, false agency. See [references/structures.md](../../references/structures.md).

3. **Name the actor.** Whoever acts is the subject. Use passive only when the thing acted on is the topic.

4. **Be specific.** No vague declaratives ("The reasons are structural"). Name the specific thing. No lazy extremes ("every," "always," "never") doing vague work.

5. **Put the reader in the room.** No narrator-from-a-distance voice. "You" beats "People." Specifics beat abstractions.

6. **Short sentences, varied rhythm.** Average 15 to 20 words. Uniform lengths are an AI tell. End paragraphs differently. No em dashes.

7. **Trust readers.** State facts directly. Skip softening, justification, hand-holding.

8. **Cut quotables.** If it sounds like a pull-quote, rewrite it.

9. **Don't argue with the reader.** State what the thing does and stop. No "not merely X," no "not just a smoke test," no "not decorative." The negation tail defends against an objection nobody raised.

10. **Don't label importance, show it.** "Load-bearing," "decisive," "the key insight," "not optional" all mean "this matters" without saying why. Name the consequence instead.

11. **Say it once.** Claim, then aphorism, then importance label states one fact three times. Keep the claim. Two items beat three. Lists and comparisons keep every real item and may repeat wording.

12. **Length follows information.** A three-character fix gets one sentence.

13. **Describe what the thing does.** Your instructions stay in the chat.

14. **Overview first, details after.**

15. **Use plain words.** See Plain Words in phrases.md.

## Quantitative check

Before delivering prose longer than ~100 words, run the slopometer:

- Command: `tools/slopometer --json` (reads stdin)
- Parse with `jq` — never `grep`/`sed` over JSON
- Exit 3: show the user the banner and stop; estimate no metrics.

Use the JSON metrics (burstiness, ttr, ai_vocabulary_density, passive_voice_rate, findings[], visual_findings[]) to prioritize edits, then re-run after revision.

## Quick Checks

Before delivering prose:

- Empty intensifier or assertion adverb ("really," "exactly," "actually," "cleanly")? Delete it.
- Passive with no actor, or a thing doing a human verb ("the decision emerges")? Name who does it.
- Sentence starts with a Wh- word? Restructure it.
- Any "here's what/this/that" throat-clearing? Cut to the point.
- Any "not X, it's Y" contrasts? State Y directly.
- Three consecutive sentences match length? Break one.
- Paragraph ends with punchy one-liner? Vary it.
- Em-dash anywhere? Remove it.
- Vague declarative ("The implications are significant")? Name the specific implication.
- Narrator-from-a-distance ("Nobody designed this")? Put the reader in the scene.
- Meta-joiners ("The rest of this essay...")? Delete. Let the essay move.
- Sentence ends in ", not merely X" or ", not just Y"? Cut the tail.
- "Load-bearing," "decisive," "the crux," "not optional"? Replace with the consequence.
- "Deliberately," "intentionally," "by design"? Every choice was. State the mechanism.
- "Silently"? Only if you checked for the log line, the warning and the exit code. Otherwise drop it.
- Telling the reader something doesn't matter ("inert," "no-op," "cosmetic," "harmless," "dead code")? Say what reads it.
- Bold phrase followed by an em-dash? Split into two sentences, drop the bold.
- Paragraph opens with a bold label and a colon? Prose doesn't need field names.
- Two or more parentheticals in one sentence? Move the evidence to the end.
- Sentence past 25 words? Find the second verb and start over there.
- Rating your own work ("clean," "surgical," "robust," "elegant")? Give the number instead.
- Reply opens with "You're right" or "Good catch"? The correction shows it.
- Asking yourself a question in quotes before answering it? Delete the question.
- "Three X, each closed/covered/measured"? Drop the count and the grade, keep the list.
- Zombie nouns ("the configuration of")? Use the verb.
- Trailing ", ensuring X"? Cut it or make it a sentence.
- Subject and verb 10+ words apart? Move them together.

Visuals: choose and review them with [references/visuals.md](../../references/visuals.md).

- Visual restates the prose? Cut it.
- Mermaid over 20 nodes, labels over 7 words, or subgraphs over 2 deep? Split and shorten.
- Emoji on a heading, bullet or diagram node? Delete it.
- Three steps in one paragraph? Number them.

## 🏆 Wall of Shame

When reviewing or diagnosing prose, surface the most ridiculous AI slop you found. Pick up to 3 worst offenders, quoted from the text. Skip this section if the text has no clear offenders. Do not invent examples.

For each offender, tag it with one emoji and a one-line roast. Roast the sentence, not the writer.

| Emoji | Offense |
|-------|---------|
| 🤖 | Robotic phrasing — sounds like a chatbot wrote it |
| 💀 | Dead cliché — "It's important to note," "In today's world" |
| 🎭 | Fake drama — manufactured urgency or gravity |
| 🪞 | Self-referential — the text talks about itself |
| 🫠 | Cringe filler — adds nothing, sounds desperate to fill space |
| 🦜 | Parrot — repeats the same idea in slightly different words |
| 🖼️ | Decorative visual: a diagram or table that restates the prose, or an emoji used as ornament |

**Format:**

> 🤖 "This comprehensive guide provides a detailed overview of the key considerations."
> → It's a list, not a comprehensive guide. Say what it covers.

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

## Examples

See [references/examples.md](../../references/examples.md) for before/after pairs and Wall of Shame entries.

## License

MIT
