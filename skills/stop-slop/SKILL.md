---
name: stop-slop
description: Remove AI tells and unclear writing. Use when you write or review text, make text clearer, or review a diagram or table.
when_to_use: "When prose has filler, clichés or rhythm issues, when text should be clearer, or when a diagram or table needs review."
---

# Stop Slop

Eliminate predictable AI writing patterns from prose.

## Core Rules

1. **Cut filler phrases.** Remove throat-clearing openers, emphasis crutches, empty intensifiers and assertion adverbs. See [references/phrases.md](../../references/phrases.md).

2. **Break formulaic structures.** When framing hides the point, state it directly. For contrasts, lists, fragments, rhetorical setups, and false agency, see [references/structures.md](../../references/structures.md).

3. **Name the actor.** Whoever acts is the subject. Use passive only when the thing acted on is the topic.

4. **Be specific.** No vague declaratives ("The reasons are structural"). Name the specific thing. No lazy extremes ("every," "always," "never") doing vague work.

5. **Name what happens.** When "People" hides who acts, name the actor and action. Use "you" when the reader acts.

6. **Short sentences, varied rhythm.** Average 15 to 20 words. Uniform lengths are an AI tell. End paragraphs differently. No em dashes.

7. **State the fact.** If a clause only reassures or justifies including a claim, cut it. Keep explanations of cause or behavior.

8. **Keep observable claims.** If a quotable sentence adds no fact, cut it; otherwise name the action or consequence.

9. **Keep needed distinctions.** When a negation tail adds no fact, cut it. For exceptions, see [Negation-as-Proof](../../references/structures.md#negation-as-proof).

10. **Name the consequence.** When "load-bearing," "decisive," "the key insight," or "not optional" only labels importance, say what changes or fails. Keep actual requirements.

11. **Say it once.** Keep each fact once; cut restatements that add no information. Lists and comparisons keep every real item and may repeat wording.

12. **Length follows information.** A three-character fix gets one sentence.

13. **Make technical documentation add information.** Explain design choices through constraints and consequences. Reference code and configuration for details readers can retrieve there. Keep needed contracts, instructions, API names, exceptions, and short examples. State triggers and outcomes with concrete actors and actions. Mark unknown rationale as unknown; code alone cannot establish historical intent.

14. **Overview first, details after.**

15. **Use plain words.** See Plain Words in phrases.md.

## Quantitative check

Before delivering prose longer than ~100 words, run the slopometer:

- Command: `../../tools/slopometer --json` (reads stdin). The path is relative to this file, like the reference links. The shell starts in the user's project, so resolve it first.
- Parse with `jq` — never `grep`/`sed` over JSON
- Exit 3: show the user the banner and stop; estimate no metrics.

Use the JSON metrics (burstiness, ttr, ai_vocabulary_density, passive_voice_rate, findings[], visual_findings[]) to prioritize edits, then re-run after revision.

## Quick Checks

Before delivering prose:

- Empty intensifier or assertion adverb ("really," "exactly," "actually," "cleanly")? Delete it.
- Passive with no actor or "the decision emerges"? Name who or what acts; software actors count.
- Wh- opener? Keep conditions and causes; rewrite empty setups. See [Sentence Starters](../../references/structures.md#sentence-starters-to-avoid).
- Any "here's what/this/that" throat-clearing? Cut to the point.
- Corrected subject or "not X, it's Y"? Review with [Binary Contrasts](../../references/structures.md#binary-contrasts).
- Three consecutive sentences match length? Break one.
- Paragraph ends with punchy one-liner? Vary it.
- Em-dash anywhere? Remove it.
- Vague declarative ("The implications are significant")? Name the specific implication.
- Distant summary ("Nobody designed this")? Name who did what; keep factual causes.
- Meta-joiners ("The rest of this essay...")? Delete. Let the essay move.
- Sentence ends in ", not merely X" or ", not just Y"? Review with [Negation-as-Proof](../../references/structures.md#negation-as-proof).
- "Load-bearing," "decisive," "the crux," "not optional"? Name the consequence; preserve actual requirements.
- "Deliberately," "intentionally," "by design"? Every choice was. State the mechanism.
- "Silently"? Only if you checked for the log line, the warning and the exit code. Otherwise drop it.
- Telling the reader something doesn't matter ("inert," "no-op," "cosmetic," "harmless," "dead code")? Say what reads it.
- Bold phrase followed by an em-dash? Split into two sentences, drop the bold.
- Paragraph opens with a bold label and a colon? Prose doesn't need field names.
- Two or more parentheticals in one sentence? Move the evidence to the end.
- Sentence past 25 words? Find the second verb and start over there.
- Rating your own work ("clean," "surgical," "robust," "elegant")? Give the number instead.
- Reply opens with "You're right" or "Good catch"? The correction shows it.
- Instruction history in the deliverable? Describe behavior; see [Compliance Narration](../../references/structures.md#compliance-narration).
- Asking yourself a question in quotes before answering it? Delete the question.
- "Three X, each closed/covered/measured"? Drop the count and the grade, keep the list.
- Zombie nouns ("the configuration of")? Use the verb.
- Trailing ", ensuring X"? Cut it or make it a sentence.
- Subject and verb 10+ words apart? Move them together.

Visuals: choose and review them with [references/visuals.md](../../references/visuals.md).

- Visual merely repeats the prose without clarifying its structure? Cut it.
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
| 🖼️ | Decorative visual: a diagram or table that repeats the explanation without clarifying structure, or an emoji used as ornament |

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
| Visual fit | Does it clarify overview, order, relationships, or comparisons? |

Below 42/60: revise.

## Examples

See [references/examples.md](../../references/examples.md) for before/after pairs and Wall of Shame entries.

## License

MIT
