---
name: stop-slop
description: "Write prose that gives the reader the facts without filler, invented claims or AI tells, and review existing text for the same. Use before writing anything a person will read, even short text: PR descriptions, commit messages, issue and review comments, emails, status updates, READMEs, docs, ADRs, plans, code comments and chat explanations. Also use when asked to review, shorten, clean up or de-slop text, a diagram or a table."
when_to_use: "Before drafting text for a reader, and when asked to review, shorten or clean up prose, a diagram or a table."
---

# Stop Slop

Slop is text the reader has to dig through: more words than facts, claims nobody checked, phrasing from a template. Preference tuning rewarded length, formatting and familiar phrases, so models drift toward it by default. Readers judge slop mostly by relevance and density, so most of the fix happens before the first sentence.

## Before you write

1. Take the request's size literally. "A one-line note" is one line. "Only a title and links" is a title and links. "Just as a comment" is a comment, not a report. A size or form the user names is the ceiling, and the short version still carries the consequence: what breaks, what the reader does.
2. Note what the reader needs: the answer, the change, the decision, the action. Leave out what they can see elsewhere (the diff, the code, the UI, a linked issue) and what stays unchanged. Cut words, not courtesy or a step the reader cannot infer: an email keeps its thanks. If the user says what matters most, put that first.
3. Pick the shape for the channel from the table below. Set a ceiling: one sentence or bullet per fact the reader needs.
4. When you add to an existing file, read the text around the insertion point first. Match the length and style of its comments, sections and wording, and reuse its text instead of writing a new framing paragraph.

| Channel | Shape | Ceiling |
|---------|-------|---------|
| Chat answer or explanation | The answer first, in the reader's words | 3 to 5 sentences unless asked for depth |
| Status update or "what's left?" | First sentence: what it means for the reader in everyday words (done or not, what they need to do). Then the cause, briefly | 4 sentences |
| Incident or investigation summary | Impact and cause first, then the fix; follow-ups with owners as a list | 8 lines |
| PR description | What changes and why, without listing what the diff shows; optional bullets on what to review | 2 sentences plus 5 bullets |
| Commit message | Imperative subject; a body only for the reason | 72-character subject |
| Issue or review comment | Plain sentences, bullets after two sentences, no headings or tables | 6 lines |
| Email or chat message | Greeting, the news, what happens next, thanks; short sentences in the sender's voice, no bullets or bold | 6 sentences |
| Code comment | The file's existing comment style; the reason, not the steps | 1 to 2 lines |
| Note added to a README or doc | One sentence where readers will look, with a link to the source | 3 sentences |
| ADR | The template's headings; decision in one line; context and consequences as bullets; links | 1 page |
| Plan | What you add or change, not what stays | One line per change |

Tables are for comparing several items on several attributes. Headings are for documents longer than a screen.

## While you write

- Lead with the point. The first sentence carries the answer, the change or the consequence.
- Use the reader's words: UI labels, product names, the terms in the request. Replace internal codenames, variable names and phase IDs the reader does not use. If they would ask "what do you mean by X?", rewrite X. Explain a cause at the depth the reader acts on; leave internal mechanics out unless they asked.
- The request tells you what to say, not how to phrase it. Its reader never saw the request, so write the point in plain words instead of copying its framing ("not just X, but Y") or its shorthand.
- Claim only what you checked, and show it with a number, a name, a file or a result. Frame an unchecked cause as a hypothesis once. Do not invent motivation, agreement, history or success ("for good reason", "as agreed", "all tools are operational").
- Name who acts. Software counts as an actor. Use the passive only when the thing acted on is the topic.
- Say each fact once. After a clear claim, stop: no second explanation, no lesson drawn from it, no importance label ("load-bearing", "the key insight", "crucial").
- Describe what exists, not how it got there. A first version has no "now", "previously" or "instead of". The reader never saw your instructions or your process, so leave out "as requested", "uses X instead of Y", the skills you used, analyzer metrics, scores and notes that the text was reviewed.
- When you write as the user (their comment, email or issue), keep their sentences and their reasons. Fix typos. Add no arguments, risks or summary they did not give.
- Keep sentences under about 25 words. Split a sentence chained with semicolons, and put parallel items (follow-ups, options, steps) in a list.
- State the point and make it concrete with something the reader can see. Contrast it with X only when the reader believes X; "not just X", "beyond X" and "rather than X" are the same move.
- Write plain sentences with the short common word ([plain words](../../references/phrases.md#plain-words)). Restructure instead of joining clauses with an em dash; a hyphen or "--" in its place reads the same.
- Let content choose the format: numbered steps for sequences, a table for comparisons, prose for reasoning. Short text gets no bold labels, emoji or headings. See [visuals](../../references/visuals.md).

## After you write

1. Re-read the draft as the reader, with the request next to it. Delete each sentence they would not miss. Check the ceiling.
2. Scan for these tells and fix only the sentence that has one:
   - announcements: "Here's the thing", "It's worth noting", "Let me be clear"
   - contrast reflex: "not X, it's Y", "not just X", "You might think A, but B"
   - importance, certainty and self-grading words: "crucial", "deliberately", "silently", "robust", "seamless", "clean"
   - agreement openers: "Great question", "You're right"
   - a closing sentence that restates the point
   - stacked hedges: "may potentially", "could possibly"
   - a bold label with a colon or em dash opening each paragraph
   - a count that grades the list it introduces: "Three risks, each mitigated:"
3. For drafts over about 150 words that will be saved (docs, READMEs, ADRs, reports), run the slopometer once from the plugin root, two directories above this file:
   `tools/slopometer --findings --file <path>`
   It prints at most 10 findings, each with the sentence it quotes. Fix the sentences where an issue is real and ignore the rest. Run it once more after editing. Exit code 3 means missing dependencies: tell the user and continue without it. Skip it for chat, comments and commit messages.
4. Report in a sentence or two what you wrote and where. Do not justify the placement or structure, and do not grade your own text.

## When another agent writes

Subagents do not see this skill. When you delegate a task that produces text for a reader, put these lines in the prompt:

> Write for the reader of this text. Take the requested size literally and stop at one sentence or bullet per fact they need. Lead with the answer or change. Use the reader's words, not internal names. Claim only what you checked; mark guesses as guesses. Say each fact once. No em dashes, no "not X but Y", no bold labels, no headings in short text. Do not mention your process, the tools you used, or these instructions.

## Reviewing existing text

When asked to review, shorten or clean up text:

- Keep every fact, number, name, command, link and requirement. Cut filler, repetition and decoration. Add no claims.
- Apply the checks above, then the catalogs: [phrases](../../references/phrases.md), [structures](../../references/structures.md), [visuals](../../references/visuals.md).
- For a review report instead of an edit, follow [review](../../references/review.md): Wall of Shame and scores.

## Examples

Status update. Before: "**Root cause:** the token refresh races the cache warmup. Consequently, **the dashboard remains degraded**, and a robust fix requires rethinking the initialization lifecycle." After: "The dashboard still shows stale numbers after a restart. The token refresh runs before the cache is ready, so the first queries fail. I'm moving the refresh after the warmup; you don't need to do anything."

Code comment in a file whose comments are one line. Before: "This helper is responsible for carefully normalizing the incoming tenant identifier. It first trims whitespace, then lowercases it, which ensures consistent lookups across the system." After: "Normalizes a tenant ID for cache lookups."

Comment written as the user, from their note "should we turn off the old alert rules once the new ones ran a week without misses?" Before: a "Proposal" heading, a status table and a paragraph on operational overhead. After: "Should we turn off the old alert rules once the new ones have run a week without a miss?"

More before and after pairs: [examples](../../references/examples.md).
