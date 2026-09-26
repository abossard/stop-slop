# Before/After Examples

## Example 1: Throat-Clearing + Binary Contrast

**Before:**
> "Here's the thing: building products is hard. Not because the technology is complex. Because people are complex. Let that sink in."

**After:**
> "Building products is hard. Technology is manageable. People aren't."

**Changes:** Removed opener, binary contrast structure, and emphasis crutch. Direct statements.

---

## Example 2: Filler + Unnecessary Reassurance

**Before:**
> "It turns out that most teams struggle with alignment. The uncomfortable truth is that nobody wants to admit they're confused. And that's okay."

**After:**
> "Teams struggle with alignment. Nobody admits confusion."

**Changes:** Cut hedging ("most"), removed throat-clearing phrases, deleted permission-granting ending.

---

## Example 3: Business Jargon Stack

**Before:**
> "In today's fast-paced landscape, we need to lean into discomfort and navigate uncertainty with clarity. This matters because your competition isn't waiting."

**After:**
> "Move faster. Your competition is."

**Changes:** Eliminated jargon entirely. Core message in six words.

---

## Example 4: Dramatic Fragmentation

**Before:**
> "Speed. Quality. Cost. You can only pick two. That's it. That's the tradeoff."

**After:**
> "Speed, quality, cost—pick two."

**Changes:** Single sentence. No performative emphasis.

---

## Example 5: Rhetorical Setup

**Before:**
> "What if I told you that the best teams don't optimize for productivity? Here's what I mean: they optimize for learning. Think about it."

**After:**
> "The best teams optimize for learning, not productivity."

**Changes:** Direct claim. No rhetorical scaffolding.

---

# Technical-Register Examples

Every "before" below is real output, quoted verbatim from a single message in an engineering blueprint or chat transcript. No invented specimens, and no fragments stitched together from separate messages.

## Example 6: Negation-as-Proof

**Before:**
> "`Run_TerminatesANonYieldingLoop_WithinTheTimeout` runs `while (true) {}` and asserts bounded elapsed time against `HealthModelScriptRuntime.Timeout`, not merely that an error came back."

**After:**
> "`Run_TerminatesANonYieldingLoop_WithinTheTimeout` runs `while (true) {}` until `HealthModelScriptRuntime.Timeout` and does not exit earlier on an error."

**Changes:** Dropped "bounded" and the "not merely" tail. The test's behaviour was already fully described before the comma.

---

## Example 7: Deliberateness + Importance Label

**Before:**
> "NOTE: memory is deliberately NOT asserted — `MemoryLimitConstraint` self-disables across thread hops (`Environment.CurrentManagedThreadId != _initialThreadId`), so timeout + statement ceiling are the load-bearing limits."

**After:**
> "Memory is not asserted, because `MemoryLimitConstraint` self-disables across threads. Only timeout and statement count limit the run."

**Changes:** Cut "deliberately," the shouted NOT, the em-dash clause, the inline field reference, and "load-bearing." Two facts, two sentences.

---

## Example 8: Restatement Escalation

**Before:**
> "The guard must fail on a mutation, not merely succeed on a clean tree. A guard only ever run against an unchanged tree is a vacuous green. The mutate-and-rerun step is the load-bearing half."

**After:**
> "Mutate the tree and rerun the guard. It has to fail."

**Changes:** Three sentences carrying one instruction, collapsed to the instruction. The aphorism and the importance label restated the first sentence.

---

## Example 9: Importance Label as Reason

**Before:**
> "This is a required, load-bearing implementation detail for C24/C29/C31, not an optional nicety."

**After:**
> "C24, C29 and C31 depend on this."

**Changes:** "Required," "load-bearing" and "not an optional nicety" all say the same thing three times. Naming the dependents says it once, with the fact attached.

---

## Example 10: Em-Dash Bold Clause

**Before:**
> "Every load-bearing live signal (C1, C3, C4a, C4b, C7, C11) was **independently observed** by this inspector — not taken from replicate — so the external-state dependency driver is mitigated."

**After:**
> "I observed C1, C3, C4a, C4b, C7 and C11 myself instead of reading them from replicate."

**Changes:** Removed the importance label, the bold, the em-dash aside, and the justification tail. Named the actor.

---

## Example 11: Verdict Opener

**Before:**
> "The key insight: **the SQL hasn't been updated to Level 1 yet** — the `DISTINCT` + `LOWER()` is still a proposal, not deployed."

**After:**
> "The SQL is still on the old level. `DISTINCT` + `LOWER()` was proposed but never deployed."

**Changes:** Cut the opener, the bold, the em-dash, and the negation tail.

---

## Example 12: Assertion Adverbs

**Before:**
> "It exactly reproduced every real corridor pick for all 7 edges and pinpointed `a->p`'s `corr(2, want=206)` call as the exact failure."

**After:**
> "It reproduced all 7 corridor picks and located the failure at `a->p`'s `corr(2, want=206)` call."

**Changes:** Two uses of "exact" removed, plus "real" and "pinpointed." Reproducing 7 of 7 already states the precision.

---

## Example 13: Self-Praise

**Before:**
> "Clean surgical diff: **1 file, +9/−33 lines.** Only two things changed:"

**After:**
> "1 file, +9/−33 lines. Two things changed:"

**Changes:** The line count already proves the size. "Clean" and "surgical" rate the work instead of describing it, and they arrive before the numbers that settle the question.

A second specimen, from a different session, grades three things and measures none:

> "All 4 fixes correct, build clean, syntax clean."

---

## Example 14: Self-Interrogation

**Before:**
> *"Anything that would make these criteria vacuous?"* Three traps, each closed explicitly: measuring the ablation on cached points instead of regenerated ones; measuring long-label containment on the shipped examples; and proving NC-30 against a library the generator wrote in the same process without a fresh decode. Each criterion above names its boundary to block exactly that.

**After:**
> "Three ways these criteria could pass without proving anything: measuring the ablation on cached points instead of regenerated ones, measuring long-label containment on the shipped examples, and proving NC-30 against a library written in the same process without a fresh decode. Each criterion names its boundary."

**Changes:** Cut the question asked to nobody, the pre-grade ("each closed explicitly"), and the closing restatement. The list remains.

---

# Real Before/After

Each pair below is the owner's own edit, quoted verbatim from the git history of a public repository. The numbers come from `tools/slopometer --json` on the quoted text without the `>` markers; "issues" counts every finding the analyzer reports. Inline code does not count as prose words.

## Example 15: Trigger Scaffolding

**Source:** minime (`abossard/virtucon`), `5b9d75be` -> `725532b5`, `skills/extract/SKILL.md`

**Before:**
> Trigger: the coherent task or session boundary has been reached with no active criteria and no blocking issue, or the user explicitly requested extract. It turns raw outcomes into durable knowledge under `raw/`, `wiki/`, and `schema.md`.

**After:**
> Turn this task's raw outcomes into durable knowledge under `raw/`, `wiki/`, and `schema.md`. Terminal phase, runs at most once.

**Changes:** Replaced the trigger with the task itself.

| | Words | Sentences | FK grade | Passive rate | Issues |
|--|------:|----------:|---------:|-------------:|-------:|
| Before | 33 | 2 | 11.58 | 0.50 | 1: passive voice with no actor |
| After | 16 | 2 | 5.23 | 0.00 | 0 |

---

## Example 16: Context Instead of Action

**Source:** Azure/azure-monitor-baseline-alerts, `191e5ae4` -> `23d41f17`, `docs/content/patterns/alz/Overview/Health-Models-Adoption.md`

**Before:**
> The current pull request gives every child model one healthy dummy entity to confirm the deployment succeeded. The diagram labels that entity as a deployment check because it does not measure domain health. Replace it with the platform and system flows the domain provides.

**After:**
> Add monitoring signals to each child model before using its state to assess domain health.

**Changes:** Dropped the history of the pull request and kept the action the reader has to take.

| | Words | Sentences | FK grade | Passive rate | Issues |
|--|------:|----------:|---------:|-------------:|-------:|
| Before | 44 | 3 | 9.71 | 0.00 | 1: plain word "provides" |
| After | 15 | 1 | 9.14 | 0.00 | 0 |

---

## Example 17: Vague Advice Into Steps

**Source:** Azure/azure-monitor-baseline-alerts, `ad3b75f4` -> `191e5ae4`, `docs/content/patterns/alz/Overview/Health-Models-Adoption.md`

**Before:**
> For each ALZ domains you might create a specific health model that represents the system flows of that domain, with the resources that contribute to it. You can use a mix of manually build entities and modelling and combine it with discovery rules for places where you don't control the life cycle of the contributing resources.

**After:**
> Combine manually modeled entities with discovery rules where resources change often. Split paths that fail independently, set the rollup behavior on each parent entity, then set an objective on the root.

**Changes:** Turned a hedged description ("you might create") into concrete steps.

| | Words | Sentences | FK grade | Passive rate | Issues |
|--|------:|----------:|---------:|-------------:|-------:|
| Before | 56 | 2 | 13.87 | 0.00 | 2: long sentences (26 and 30 words) |
| After | 31 | 2 | 11.39 | 0.00 | 1: plain word "objective" |

---

## Example 18: Checklist Language

**Source:** minime (`abossard/virtucon`), `5b9d75be` -> `725532b5`, `skills/replicate/SKILL.md`

**Before:**
> - Tick `[x]` on the criterion when its test goes green. **Do this immediately. Do not batch check-offs for later.**
> - Paste raw shortened evidence (command output, test result, key lines) directly under the criterion line. Every `[x]` must have its proof inline — a checkmark without evidence is not a checkmark.
> - If you resolve an unknown during implementation, add it to the Decisions table with its VOI level and source.
> - If you discover a requirement not in the original EARS, note it but do NOT add it to the criteria. That's review's job.
> - Work only on the current correction's active criteria. Archived criteria remain out of scope unless the blueprint marks their baseline proof invalidated.

**After:**
> - Tick `[x]` the moment its test goes green. **Do not batch check-offs for later.**
> - Paste raw shortened evidence (command output, test result, key lines) directly under the criterion line. A checkmark without inline proof is not a checkmark.
> - Add any unknown you resolved to the Decisions table with its VOI level and source.
> - Note a requirement you discover outside the original EARS, and leave it out of the criteria. Inspect owns that call.
> - Work only on the current correction's active criteria. Archived criteria stay out of scope unless the blueprint marks their baseline proof invalidated.

**Changes:** Cut "immediately", the em-dash aside and the "If you..." openers; each bullet now starts with its verb.

| | Words | Sentences | FK grade | Passive rate | Issues |
|--|------:|----------:|---------:|-------------:|-------:|
| Before | 111 | 10 | 7.98 | 0.00 | 2: plain words "immediately", "requirement" |
| After | 94 | 9 | 7.31 | 0.00 | 1: plain word "requirement" |

---

## Example 19: Wh- Opener

**Source:** Azure/azure-monitor-baseline-alerts, `ad3b75f4` -> `191e5ae4`, `docs/content/patterns/alz/Overview/Health-Models-Adoption.md`

**Before:**
> What it does not carry is dependency. Every alert rule is deployed independently of every other one, so nothing in the system knows that an ExpressRoute circuit, a firewall and a gateway are three parts of one connectivity service. Three alerts fire, and a human decides whether that adds up to an outage.

**After:**
> AMBA-ALZ does not model dependencies between alert rules. An ExpressRoute circuit, a firewall, and a gateway can support one connectivity service, but their alerts remain independent. An operator must assess their combined effect.

**Changes:** Put the subject first instead of "What it does not carry", split the 32-word sentence, and named the operator who judges the alerts.

| | Words | Sentences | FK grade | Passive rate | Issues |
|--|------:|----------:|---------:|-------------:|-------:|
| Before | 53 | 3 | 10.45 | 0.33 | 2: long sentence (32 words), passive voice with no actor |
| After | 33 | 3 | 10.87 | 0.00 | 0 |

---

## Example 20: Slogan Labels

**Source:** Azure/azure-monitor-baseline-alerts, `ad3b75f4` -> `191e5ae4`, `docs/content/patterns/alz/Overview/Health-Models-Adoption.md`

**Before:**
> - **Fewer alerts, not fewer measurements.** Alerting moves from every rule to the entities you decide matter, so notification volume tracks the number of real problems rather than the size of the estate.
> - **Criticality is expressed once, in the graph.** A dependency says which components a service actually needs, so importance comes from position in the graph instead of a severity set per rule.
> - **Recovery is visible, and measurable.** You see when something clears, and how long it was broken.

**After:**
> - **Consolidated alerts.** Multiple signals determine one entity state. An alert on that entity fires once when its state changes to degraded or unhealthy.
> - **Explicit dependencies.** Relationships describe which components a service depends on and how their health affects the parent entity.
> - **Health history.** Graph and timeline views show current and past entity states.

**Changes:** Replaced slogan labels ("Fewer alerts, not fewer measurements") with feature names, cut "actually", and made each bullet say what the feature does.

| | Words | Sentences | FK grade | Passive rate | Issues |
|--|------:|----------:|---------:|-------------:|-------:|
| Before | 79 | 3 | 9.26 | 0.67 | 4: long sentences (32 and 31 words), 2 passives with no actor |
| After | 53 | 4 | 11.17 | 0.00 | 0 |

---

## Example 21: Em-Dash Join

**Source:** minime (`abossard/virtucon`), `2e859b26` -> `e4259718`, `assets/ORCHESTRATION.md`

**Before:**
> `harvest` also reads the persisted task brief's Decisions table and "Discovered during review" section to learn what categories of criteria the EARS consistently misses — that meta-learning feeds the director's process memory and sharpens future EARS nudges.

**After:**
> `harvest` also reads the persisted task brief's Decisions table and "Discovered during review" section to learn what categories of criteria the EARS consistently misses. That meta-learning feeds the director's process memory and sharpens future EARS nudges.

**Changes:** Split the em-dash clause into its own sentence.

| | Words | Sentences | FK grade | Passive rate | Issues |
|--|------:|----------:|---------:|-------------:|-------:|
| Before | 35 | 1 | 20.31 | 0.00 | 1: long sentence (35 words) |
| After | 35 | 2 | 13.49 | 0.00 | 0 |

---

# Wall of Shame Entries

More entries in the format `skills/stop-slop/SKILL.md` defines.

> 💀 "It's important to note that security plays a crucial role."
> → Everything in a security doc is important to note. Cut the throat-clearing.
>
> 🎭 "In an era of unprecedented digital transformation, organizations must navigate..."
> → Nobody talks like this. Say what changed and what to do about it.
