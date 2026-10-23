# Review

Use this file when the user asks for a review of existing text, a report or a score, not only a rewrite. Keep every fact when you edit.

## Checklist

Review with these checks after the ones in [SKILL.md](../skills/stop-slop/SKILL.md#after-you-write).

- Empty intensifier or assertion adverb ("really," "exactly," "actually," "cleanly")? Delete it.
- Passive with no actor or "the decision emerges"? Name who or what acts; software actors count.
- Wh- opener? Keep conditions and causes; rewrite empty setups. See [Sentence Starters](structures.md#sentence-starters-to-avoid).
- Any "here's what/this/that" throat-clearing? Cut to the point.
- Corrected subject or "not X, it's Y"? Review with [Binary Contrasts](structures.md#binary-contrasts).
- Three consecutive sentences match length? Break one.
- Paragraph ends with punchy one-liner? Vary it.
- Em-dash anywhere? Remove it.
- Vague declarative ("The implications are significant")? Name the specific implication.
- Distant summary ("Nobody designed this")? Name who did what; keep factual causes.
- Meta-joiners ("The rest of this essay...")? Delete. Let the essay move.
- Sentence ends in ", not merely X" or ", not just Y"? Review with [Negation-as-Proof](structures.md#negation-as-proof).
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
- Instruction history in the deliverable? Describe behavior; see [Compliance Narration](structures.md#compliance-narration).
- Asking yourself a question in quotes before answering it? Delete the question.
- "Three X, each closed/covered/measured"? Drop the count and the grade, keep the list.
- Zombie nouns ("the configuration of")? Use the verb.
- Trailing ", ensuring X"? Cut it or make it a sentence.
- Subject and verb 10+ words apart? Move them together.

Visuals: choose and review them with [references/visuals.md](visuals.md).

- Visual merely repeats the prose without clarifying its structure? Cut it.
- Mermaid over 20 nodes, labels over 7 words, or subgraphs over 2 deep? Split and shorten.
- Emoji on a heading, bullet or diagram node? Delete it.
- Three steps in one paragraph? Number them.

## Wall of Shame

When reviewing or diagnosing prose, surface the most ridiculous AI slop you found. Pick up to 3 worst offenders, quoted from the text. Skip this section if the text has no clear offenders. Do not invent examples.

For each offender, tag it with one emoji and a one-line roast. Roast the sentence, not the writer.

| Emoji | Offense |
|-------|---------|
| 🤖 | Robotic phrasing: sounds like a chatbot wrote it |
| 💀 | Dead cliché: "It's important to note," "In today's world" |
| 🎭 | Fake drama: manufactured urgency or gravity |
| 🪞 | Self-referential: the text talks about itself |
| 🫠 | Cringe filler: adds nothing, sounds desperate to fill space |
| 🦜 | Parrot: repeats the same idea in slightly different words |
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
