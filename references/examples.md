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
