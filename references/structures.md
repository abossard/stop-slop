# Structures to Avoid

## Binary Contrasts

Formulaic contrasts create false drama. State the point directly.

| Pattern | Problem |
|---------|---------|
| "Not because X. Because Y." / "Not because X, but because Y." | Telegraphed reversal |
| "[X] isn't the problem. [Y] is." | Formulaic reframe |
| "The answer isn't X. It's Y." | Predictable pivot |
| "It feels like X. It's actually Y." | Setup/reveal cliche |
| "The question isn't X. It's Y." | Rhetorical misdirection |
| "Not X. But Y." / "not X, it's Y" / "isn't X, it's Y" | Mechanical contrast |
| "It's not this. It's that." | Same formula, different words |
| "stops being X and starts being Y" | False transformation arc |
| "doesn't mean X, but actually Y" | Negation-then-assertion crutch |
| "is about X but not Y" | False distinction |
| "not only X but also Y" / "not just X but also Y" | Additive: use "X and Y" |

**Instead:** State Y directly when the rejected X adds nothing for the reader. Keep contrasts needed for requested comparisons, safety warnings, factual scope limits, or correcting known reader misconceptions.

Apply a user's correction to the subject; replace its superseded premise unless the reader needs the distinction:

> "Catching Birds NOT with a Lasso, but with a Net" → "Catching Birds with a Net"

## Negative Listing

Rejected alternatives can add a factual limit or only delay the point.

| Pattern | Problem |
|---------|---------|
| "Not a X... Not a Y... A Z." | Dramatic buildup through negation |
| "It wasn't X. It wasn't Y. It was Z." | Same structure, past tense |

**Instead:** Lead with Z. Keep factual exclusions; review them using [Binary Contrasts](#binary-contrasts).

## Dramatic Fragmentation

Sentence fragments for emphasis read as manufactured profundity.

| Pattern | Problem |
|---------|---------|
| "[Noun]. That's it. That's the [thing]." | Performative simplicity |
| "X. And Y. And Z." | Staccato drama |
| "This unlocks something. [Word]." | Artificial revelation |

**Instead:** Complete sentences. Trust content over presentation.

## Rhetorical Setups

These announce insight rather than deliver it.

| Pattern | Problem |
|---------|---------|
| "What if [reframe]?" | Socratic posturing |
| "Here's what I mean:" | Redundant preview |
| "Think about it:" | Condescending prompt |
| "And that's okay." | Unnecessary permission |

**Instead:** Make the point. Let readers draw conclusions.

## Formulaic Constructions

| Pattern | Problem |
|---------|---------|
| "By the time X, I was Y." | Keep when it states timing; revise if it only frames a reveal. |
| "X that isn't Y" | Keep a factual exclusion; otherwise name what X does. |

## False Agency

When an abstraction hides who acts, name the actor. Software components are actors when they perform the stated action.

| Pattern | Problem |
|---------|---------|
| "a complaint becomes a fix" | The complaint did nothing. Someone fixed it. |
| "a bet lives or dies in days" | Bets don't have lifespans. Someone kills the project or ships it. |
| "the decision emerges" | Decisions don't emerge. Someone decides. |
| "the culture shifts" | Cultures don't shift on their own. People change behavior. |
| "the conversation moves toward" | Conversations don't move. Someone steers. |
| "the data tells us" | Data sits there. Someone reads it and draws a conclusion. |
| "the market rewards" | Markets don't reward. Buyers pay for things. |

**Instead:** Name who or what acts. "The team fixed it that week" beats "the complaint becomes a fix." Use "you" when the reader acts.

## Narrator-from-a-Distance

When a summary hides who does what, name the actor and action. Keep explanations that identify an actual cause.

| Pattern | Problem |
|---------|---------|
| "Nobody designed this." | Disembodied observation |
| "This happens because..." | Keep when it explains the cause. |
| "This is why..." | Keep a cause or consequence; cut an empty announcement. |
| "People tend to..." | Armchair sociologist |

**Instead:** Name the actor and action. Use "you" only for the reader's actions; "You don't sit down one day and decide to..." needs that context.

## Passive Voice

Name the actor. A passive with no "by" phrase hides who acted; `tools/analyze.py` flags it as `Passive voice with no actor`.

| Pattern | Fix |
|---------|-----|
| "X was created" | Name who created it |
| "It is believed that" | Name who believes it |
| "Mistakes were made" | Name who made them |
| "The decision was reached" | Name who decided |

**Instead:** Find the actor. Put them at the front of the sentence. When the thing acted on is the paragraph's topic, keep the passive and name the actor in a "by" phrase.

## Sentence Starters to Avoid

| Pattern | Fix |
|---------|-----|
| Sentences starting with What, When, Where, Which, Who, Why, How | Keep conditions, causes, and direct questions; remove empty setups. |
| Paragraphs starting with "So" | Start with content |
| Sentences starting with "Look," | Remove |

Keep openers that identify a condition or cause. "What makes this hard is..." becomes "The constraint is..." or better, name the specific constraint.

## Rhythm Patterns

| Pattern | Fix |
|---------|-----|
| Three-item lists | Keep every factual item; remove only padding or repetition. |
| Questions answered immediately | Let questions breathe or cut them |
| Every paragraph ends punchily | Vary endings |
| Em-dashes | Remove. Use commas or periods. No em dashes at all. |
| Staccato fragmentation | Don't stack short punchy sentences |
| "Not always. Not perfectly." | Hedging disguised as reassurance |

## Word Patterns

| Pattern | Problem |
|---------|---------|
| Lazy extremes (every, always, never, everyone, everybody, nobody) | False authority. Use specifics instead of sweeping claims. |
| Empty intensifiers ("really," "just," "literally," "honestly," "simply") | Empty emphasis. See the Adverbs section of phrases.md for the full list. |

## Sycophantic Openers

Agreement before content. A measured artifact of preference tuning: reward models favour responses that match the user's stated view ([arXiv:2310.13548](https://arxiv.org/abs/2310.13548)).

| Pattern | Problem |
|---------|---------|
| "You're absolutely right, ..." | Validation before information |
| "You're right to call that out." | Praises the question instead of answering it |
| "Great question!" | Filler; the question needs an answer, not a rating |
| "That's a sharp insight." | Flattery dressed as analysis |

**Instead:** answer. If the user was right, the corrected answer already shows it.

## Throat-Clearing Preamble

Metadiscourse announcing that content is coming. LLM text skews toward interactive metadiscourse (transitions, frame markers) and away from genuine stance (Jiang & Hyland, *ESP* 2025).

| Pattern | Problem |
|---------|---------|
| "Let me be honest," | Implies the rest was not |
| "I need to be brutally honest with you here." | Manufactured gravity |
| "To be clear," | Usually precedes the first clear thing said |
| "Here's the thing:" | Pure runway |
| "Let's unpack this." | Announces analysis instead of doing it |

**Instead:** state the point. Delete the runway.

## Hedge Stacking

Two or more hedges within a short window (1–2 sentences). AI text hedges compulsively because it's trained to avoid definitive claims. Humans commit.

| Pattern | Problem |
|---------|---------|
| "may potentially" | Double hedge |
| "often tends to" | Double hedge |
| "could possibly" | Double hedge |
| "might sometimes" | Double hedge |
| "typically might" | Double hedge |
| "It is possible that... may..." | Hedge sandwich |
| "While it may... it could also..." | Both sides hedged |
| "arguably... perhaps... in some cases" | Triple hedge in one thought |

**Hedge words to watch:** may, might, could, possibly, potentially, perhaps, arguably, typically, often, generally, tends to, in some cases, it is possible that, it is likely that, to some extent, more or less.

**Rule:** One hedge per claim maximum. If you hedge, commit to the hedge: "X is possible" is fine. "X could potentially be possible in some cases" is AI. Pick the strongest version of what you mean and say it.

## Symmetric List Bloat

AI loves balanced, parallel structures — especially three items where each gets equal treatment regardless of importance.

| Pattern | Problem |
|---------|---------|
| "First, ... Second, ... Third, ..." with identical paragraph lengths | Mechanical enumeration |
| "On one hand... On the other hand... Additionally..." | Symmetric padding |
| Headers like "Benefits", "Challenges", "Future Directions" each with 3 equal sub-bullets | Template-driven structure |
| Every list has exactly 3 items | Artificial completeness |

**Instead:** Vary list lengths. Give more space to things that deserve it. Two items are fine. One item is fine. Not everything needs a counterpoint.

## Negation-as-Proof

A denial after a claim can restate it or add a needed limit. Check which it does before editing.

Review tails such as "not merely X," "not just a smoke test," and "not decorative" for a constraint or factual distinction.

| Pattern | Problem |
|---------|---------|
| "asserts bounded elapsed time, not merely that an error came back" | Cut only if the weaker check is irrelevant to the reader. |
| "the guard must fail on a mutation, not merely succeed on a clean tree" | Keep if mutation failure distinguishes the required check. |
| "asserts on the engine's produced error, not on a config flag" | Keep if readers might confuse the observed error with a config flag. |
| "proves detection, not just green-by-default" | Cut only if the tail adds no test requirement. |
| "a real assertion, not a smoke test" | State the assertion; keep a smoke-test comparison if requested. |

**Instead:** Cut a tail only if it adds no fact. Keep constraints, exceptions, and needed distinctions; see [Binary Contrasts](#binary-contrasts). For a redundant tail, state what happens: `Run_TerminatesANonYieldingLoop_WithinTheTimeout` runs `while (true) {}` and asserts elapsed time against `HealthModelScriptRuntime.Timeout`.

## Restatement Escalation

The same fact stated three times: as a plain claim, then as an aphorism, then as an importance label. The second and third add words without adding information.

> "The guard must fail on a mutation, not merely succeed on a clean tree. A guard only ever run against an unchanged tree is a vacuous green. The mutate-and-rerun step is the load-bearing half."

All three carry one instruction: **"Mutate the tree and rerun the guard. It has to fail."**

| Stage | Tell |
|-------|------|
| 1. Claim with a negation tail | "X, not merely Y" |
| 2. Generalised aphorism | "A guard only ever run against X is a vacuous green" |
| 3. Importance label | "The mutate-and-rerun step is the load-bearing half" |

**Instead:** Keep the claim and any distinct constraints or exceptions; cut repeated paraphrases and importance labels. For a negation tail, use [Negation-as-Proof](#negation-as-proof).

## Em-Dash Bold Clause

The highest-volume tell in technical output: 13,262 sentences, 15.2% of the audited chat corpus. Bold a noun phrase, em-dash, then gloss it.

| Pattern | Problem |
|---------|---------|
| "**Conflicts move to the right place** — the storage implementation knows how to resolve them." | Two independent sentences fused by punctuation |
| "Now it's a **Cosmos 400 BadRequest** — that's an application-level issue, not infra." | Bold + em-dash + negation tail stacked |
| "**Files with open handles** — a routine state on any file server — continuously generate errors." | Nested appositive, unreadable aloud |

**Instead:** two sentences, no bold. "Conflicts move to the storage implementation. It owns the state, so it resolves them."

## Bold-Label Colon

Turning prose into a pseudo-form: 13.6% of chat sentences open this way. Every paragraph gets a field name, so nothing reads as connected argument.

> **Root cause:** The tool passes step values directly from the JSON.
> **Conclusion:** Dapr appears in ADRs as a considered alternative.
> **Recommendation:** Keep the gateway on HTTP.

**Instead:** in a table or a form, use the label. In prose, drop it. "The tool passes step values straight from the JSON."

## Parenthetical Proof-Stuffing

Citations, counts, and file paths crammed mid-sentence so the claim can't be read without stepping over its own evidence. 11.7% of blueprint sentences and 12.2% of chat sentences carry two or more parentheticals.

> "`bundlePieces`' shared/unique split (`:908-932`, built fresh inside `for (const b of bundlePlans)`) and `collectVerticals()`'s pill-avoidance registry (`:934-970`, explicitly commented at `:949` as "never a correctness gate") are each scoped to one bundle's own membership only."

**Instead:** claim first, evidence after. Put line references at the end of the sentence or on their own line.

## Sentence Bloat

Nearly one sentence in ten runs past 40 words, in both corpora (9.9% each). One chat sentence in eighteen passes 60. Most are semicolon-chained clause stacks with parenthetical asides.

**Rule:** at 30 words, look for the second verb and start a new sentence there. Semicolons chaining three or more clauses mean the sentence should have been a list.

## Self-Interrogation

Quoting a question to yourself, then answering it with the answer already graded as complete. The question makes the answer look like the result of checking rather than a claim. 60 instances across 265 blueprints, always in the same italic-quoted shape.

> *"Anything that would make these criteria vacuous?"* Three traps, each closed explicitly: measuring the ablation on cached points instead of regenerated ones; measuring long-label containment on the shipped examples; and proving NC-30 against a library the generator wrote in the same process without a fresh decode. Each criterion above names its boundary to block exactly that.

The passage makes four moves:

| Move | Tell |
|------|------|
| Quoted question to self | *"Anything that would make these criteria vacuous?"* |
| Count with a grade attached | "Three traps, each closed explicitly" |
| Semicolon list doing the actual work | the only part a reader needs |
| Closing restatement | "Each criterion above names its boundary to block exactly that." |

**After:**
> "Three ways these criteria could pass without proving anything: measuring the ablation on cached points instead of regenerated ones, measuring long-label containment on the shipped examples, and proving NC-30 against a library written in the same process without a fresh decode. Each criterion names its boundary."

**Rule:** drop the question, drop the grade ("explicitly," "each closed," "exactly that"), keep the list.

## Count-and-Close

Announcing how many items follow and that all of them are handled, before the reader can check either claim. 26 instances in the same corpus: "Two ways, both closed:", "Four things, each a named FAIL:", "five clauses, each measured:".

| Pattern | Problem |
|---------|---------|
| "Three traps, each closed explicitly:" | Pre-grades the list it introduces |
| "Two gaps remain, both documented:" | "Documented" is not "fixed" |
| "Four decisions, all decided-by-data:" | Label substitutes for the data |
| "Each of these is covered by a test." | Name the tests or cut the sentence |

**Instead:** list the items. The reader can count them and judge whether they're closed.

## Justification Tails

Appending the reason the previous clause was written, in the same sentence.

| Pattern | Fix |
|---------|-----|
| "..., so the external-state dependency driver is mitigated" | Delete. The observation already showed it. |
| "..., which is why C1-5 lands before C1-6" | New sentence, or cut |
| "That is what proves the other three roots load-bearing" | State what the three roots do |
| "..., so timeout and statement ceiling are the load-bearing limits" | "Only timeout and statement count limit the run." |

## Compliance Narration

Writing the instructions you received into the deliverable. The doc's reader never saw the instruction, so the rejected alternative answers a question they did not ask.

The user had asked for pure functions and no state-machine framework. The agent then wrote this into the docs:

> "The implementation uses records, enums, and pure functions instead of a general state-machine framework. The plan itself describes the states and dependencies."

| Pattern | Fix |
|---------|-----|
| "uses X instead of Y" | "uses X", then say what X does |
| "The plan itself describes..." / "the prompt requires..." | Describe the behavior itself |

**Instead:** describe what the thing does. Apply corrections before drafting. Keep correction history only if it informs the reader; see [Binary Contrasts](#binary-contrasts). Record weighed alternatives in a decision record.
