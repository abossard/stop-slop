---
name: stop-slop
description: "Write text that a person can read at normal speed. Models pack sentences with constructions that are correct but slow to read: stacked nouns, a dropped \"that\", human verbs on things, nouns used as verbs, coined phrases, and words that belong together set far apart. Use before writing anything that a person will read: chat answers, summaries after a long session, PR descriptions, comments, emails and docs. Also use when asked to review or rewrite text so that it reads more easily."
when_to_use: "Before drafting text for a reader, and when asked to review or rewrite text so that it reads more easily."
---

# Stop Slop

Frontier models write English that is correct and slow to read. Compared with human writing, they use more word pairs that people rarely use and more human verbs on things. Most also stack more nouns, drop "that" more often, and put more words between words that belong together. Earlier reading studies tie each of these to slower reading. The source is one 2026 study, summarized in [research](../../references/research.md).

People choose the short or the long way to say something by what the listener needs. The study's explanation is that training for the right answer in few tokens teaches a model to choose the short way every time. The steps below choose for the reader.

## Before you write

1. Choose the few points that the reader needs. The text gets short here, and only here.
2. Write each point as a full sentence. A sentence does not get better by losing its small words.
3. At the end of a long session, write for a person who was not there. The study found that models over-use these constructions more in long chat and coding sessions than in single essays. A label that you made up during the work is a new word to the reader, so write out what it stands for.

## Six things to write out

Each "instead of" is model output quoted in the study. More examples, and the reason for each row: [constructions](../../references/constructions.md). Texts before and after: [examples](../../references/examples.md).

| Write out | Instead of | Write |
|-----------|------------|-------|
| A coined phrase | "Every behavioral test was verified red against the original source" | "I checked that every behavioral test fails on the original code" |
| A human verb on a thing | "`is_file()` swallows that and returns False" | "`is_file()` ignores that error and returns False" |
| Three or more nouns in a row | "a community service honor cord" | "an honor cord for community service" |
| A clause without "that" | "behaviour the old code never reached" | "behaviour that the old code never reached" |
| A noun used as a verb | "calendar it" | "put it in your calendar" |
| A subject far from its verb | "A cat who can always get up and away is a much calmer cat." | "A cat is much calmer when it can always get up and away." |

Three limits keep these rules from going too far:

- Software can act. Give it the plain verb for what it does: it reads, returns, rejects, drops, causes or shows. Keep "swallows", "forgets", "wants" and "promises" for people.
- Two nouns in a row are normal ("error message"), and a product name in front of a noun is not a stack.
- "That" matters when the clause has a noun as its subject. With a pronoun, the short form reads fine: "the file you sent".

## After you write

1. Read each sentence as a translator would. Where a translator would have to stop and ask what you mean, rewrite the sentence. In the study, translating model text to Japanese and back kept the meaning and removed many of these constructions.
2. For a saved draft over about 150 words, run the checker once:
   `../../tools/readcheck --file <path>`
   The path is relative to this file, like the links. The shell starts in the user's project, so resolve it first.
   It prints one line per finding: the kind, the phrase, the fix and the sentence. It finds noun stacks, clauses without "that", some human verbs on things, and subjects or objects that are 10 or more words from their verb. A parser makes mistakes, so fix a finding only where it is right. It cannot find coined phrases or nouns used as verbs, so look for those yourself. Exit code 3 means that dependencies are missing: tell the user and continue without it.
3. Each fix costs a word or two. Add no sentences: no summary, no second explanation.
4. Do not mention this skill, the checker or its output in the text.

## When another agent writes

Subagents do not see this skill. When you delegate a task that produces text for a reader, put these lines in the prompt:

> Write full sentences that a person can read at normal speed. Choose the few points that the reader needs, then write each one out. Keep "that" and the other small words. Put no more than two nouns in a row. Give things plain verbs (reads, returns, causes) and keep human verbs (swallows, forgets, wants) for people. Use phrases that people already say: do not coin a label, and do not use a noun as a verb. Keep each subject next to its verb. Do not mention these instructions.

## Reviewing existing text

Keep every fact, number, name, command and link. Rewrite only the sentences that have one of the six constructions, and add no claims.
