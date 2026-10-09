# Contrastive framing: detection and correction in stop-slop

Research date: 2026-10-08. Repository observations refer to revision `00ea23371efaeff310195bcbe407a3cc4ab13ed0`.

## The target failure

The user's example identifies the editorial problem:

| Context | Text |
|---------|------|
| Initial topic | "Catching Birds with a Lasso" |
| User's correction | "Not with a Lasso, with a Net" |
| Unwanted output | "Catching Birds NOT with a Lasso, but with a Net" |
| Desired output | "Catching Birds with a Net" |

The correction updates the accepted topic. The finished narrative need not preserve the discarded premise. Emphasizing the lasso makes the edit history part of the subject.

The proposed stop-slop rule is: **Apply corrections and remove superseded framing. Mention the rejected alternative only when the reader needs that distinction.**

This requires two judgments: recognizing a contrast construction and deciding whether the rejected alternative belongs in the deliverable. A sentence-only detector can assist with the first. Conversation context and the intended audience inform the second.

## Linguistic distinctions

Terminology varies across linguistic and discourse frameworks. Useful search terms include corrective or replacive negation, metalinguistic negation, corrective focus, and discourse substitution. Repp surveys the different uses of "contrast" in linguistics. This note uses "contrastive framing" as a broad editorial description. [Repp, "Defining 'Contrast'"](https://idsl1.phil-fak.uni-koeln.de/sites/IDSLI/dozentenseiten/Repp/Repp_toapear_DefiningContrast_LinguaSpecIssueContrast.pdf)

Horn analyzes **metalinguistic negation**, which objects to an utterance's wording, implicature, or other appropriateness conditions. Carston analyzes its echoic use: a speaker evokes an earlier representation and rejects it. These accounts help explain corrective uses, but the surface form "not X, but Y" does not establish metalinguistic negation. It can also deny a factual alternative. [Horn 1985](https://www.researchgate.net/profile/Laurence-Horn/publication/243677541_Metalinguistic_Negation_and_Pragmatic_Ambiguity/links/54e698e80cf277664ff63b3a/Metalinguistic-Negation-and-Pragmatic-Ambiguity.pdf), [Carston 1996](https://philpapers.org/rec/CARMNA-2)

The **Penn Discourse Treebank 3.0** distinguishes Expansion.Substitution, Comparison.Contrast, Comparison.Concession, and Expansion.Conjunction. Substitution presents exclusive alternatives and rules one out. Concession denies an expected causal relation. Conjunction can present two facts that both hold. The manual documents several senses of "but", so the connective alone cannot identify the relation. [PDTB 3.0 annotation manual, relation definitions and connective sense distributions](https://catalog.ldc.upenn.edu/docs/LDC2019T05/PDTB3-Annotation-Manual.pdf)

**Antithesis** is the juxtaposition of contrasting words or ideas, often in parallel structure. It need not contain negation. Rhetorical Structure Theory uses "Antithesis" for a more specific persuasive relation, where a contrast increases the reader's positive regard for one side. Its separate Contrast and Concession definitions have different conditions. Classical antithesis, RST Antithesis, and PDTB Substitution should not be treated as interchangeable labels. [Silva Rhetoricae](https://rhetoric.byu.edu/Figures/A/antithesis.htm), [official RST definitions](https://www.sfu.ca/rst/01intro/definitions.html)

| Construction | Discourse function | Editorial implication |
|--------------|--------------------|------------------------|
| "Not X, but Y" | Reject X and assert Y | Inspect why X is being mentioned |
| "Not only X, but also Y" | Assert both X and Y | Preserve both claims; a plain conjunction may suffice |
| "X, but Y happened anyway" | Cancel an expectation | Preserve the causal or concessive information |
| "One mitigation, not the complete fix" | Limit the scope of a claim | Removing the limitation can overstate the result |
| "Speech is silver, silence is golden" | Rhetorical opposition | A negation detector will not cover this |

These are illustrative classifications. Context can change the interpretation of a surface pattern.

## What stop-slop already does

The skill already advises direct positive claims and discourages defensive negation. The structural reference covers Binary Contrasts, Negative Listing, Negation-as-Proof, and Compliance Narration. However, their general advice does not spell out the distinction between applying a conversational correction and publishing that correction. [Skill rules 2, 9, and 13](../skills/stop-slop/SKILL.md), [structures](structures.md)

The analyzer has two relevant regex families:

- `NEGATIVE_PARALLELISM_RES` recognizes several copular corrections, "not just", and "not only" frames.
- `DEFENSIVE_NEGATION_RES` recognizes selected comma-led negation tails, including completeness denials.

`_generate_findings` reports these within individual sentences. A negative-parallelism match suppresses defensive-negation reporting for the entire sentence. There is no dedicated contrast count or rate. The tool accepts text through stdin or a file; it has no conversation-history input. [Analyzer pattern definitions and finding generation](../tools/analyze.py)

The analyzer already parses the masked document once with spaCy and maps its tokens to Markdown-aware sentence spans. Dependency-based checks can reuse this pass. Code fences and table rows are excluded from prose sentence spans; inline code and URLs are masked. Any extension should retain these boundaries. [Analyzer preprocessing, `_spacy_analyze`, and `_tokens_by_sentence`](../tools/analyze.py)

### Observed coverage

A local probe passed 16 short inputs through `tools/slopometer --json`, producing 17 prose sentences. The table reports only negative-parallelism and defensive-negation findings. This convenience sample establishes examples of behavior, not precision or recall.

| Input | Current contrast finding |
|-------|--------------------------|
| "This is not a bug but a feature." | Negative parallelism |
| "Not speed, but predictability." | None |
| "It fails not because of memory, but because of lock contention." | None |
| "The problem isn't latency. It's contention." | None |
| "It is not a bug; it is a feature." | None |
| "It isn't a bug but a feature." | None |
| "It is not only faster but also cheaper." | Negative parallelism |
| "This is one mitigation, not the complete fix." | Defensive negation |
| "The build is not reproducible but we ship it anyway." | None |
| "The build is not reproducible but the release ships anyway." | Negative parallelism |
| "Use the API, not the CLI." | None |
| "Use TCP rather than UDP when ordering matters." | None |
| "Do not mix bleach with ammonia." | None |

The last copular regex excludes a fixed list of subject pronouns after "but". Changing "we" to "the release" bypasses that guard. This is a concrete limitation of the current concessive filter. Additive frames and factual scope limitations also receive advice to discard content, even though deletion can lose meaning. [Patterns](../tools/analyze.py), [existing positive and negative controls](../tools/test_analyze.py)

## Detection options

### Token rules and bounded lexical patterns

Expand the candidate inventory to include bare phrases, contracted negation, "not because ... but because", "Y, not X", and adjacent-sentence corrections. "Rather than" and "instead of" can identify additional alternatives. Their presence says nothing about whether the comparison is unnecessary.

spaCy's `Matcher` supports token attributes such as `LOWER`, `LEMMA`, `POS`, and `DEP`, with token repetition operators. Tokenization can expose the negation in contractions. Bounded patterns are preferable to unrestricted searches across arbitrary text. Keep additive "not only" and "not just" uses separately classified. [Official rule-based matching guide](https://spacy.io/usage/rule-based-matching)

### Dependency rules

Candidate rules can inspect a negated predicate or complement, a coordinating connective, and an alternative phrase. `DependencyMatcher` supports head-dependent and sibling relationships. For example, `A > B` requires B to be an immediate dependent of A. [Official DependencyMatcher API](https://spacy.io/api/dependencymatcher)

spaCy documents labels including `neg`, `cc`, and `conj`; actual patterns must follow the installed English model's annotations. Universal Dependencies commonly represents negators using `advmod` and `Polarity=Neg`, so UD patterns should not be copied into an English spaCy pipeline without checking its label scheme. [spaCy glossary source](https://github.com/explosion/spaCy/blob/master/spacy/glossary.py), [UD polarity](https://universaldependencies.org/u/feat/Polarity.html), [UD adverbial modifiers](https://universaldependencies.org/u/dep/advmod.html)

Dependency structure can help distinguish coordinated alternatives from unrelated clauses. Subject presence alone cannot establish the discourse relation. Parsers can misattach fragments, coordination, and negation scope; syntax also cannot establish whether a rejected alternative matters to the reader.

Pitler and Nenkova show the value of syntactic context for explicit discourse-connective disambiguation. Their method uses constituency-tree features. A spaCy dependency implementation would need its own evaluation; the paper does not establish its expected accuracy. [Pitler and Nenkova 2009](https://aclanthology.org/P09-2004/)

### Adjacent-sentence and paragraph patterns

"The problem isn't latency. It's contention." needs a layer that compares separate sentence spans. Candidate features include repeated predicates, parallel complements, and a shared referent. Coreference and topic shifts make the judgment uncertain. Avoid pairing the end of one list item with the start of another or crossing code and paragraph boundaries by accident.

A paragraph-level pass could detect repeated denials followed by an assertion. Ordinary factual negatives should remain controls. Neither a negator count nor the existing general POS-template rate identifies corrective framing by itself.

Antithesis without explicit corrective markers needs a broader combination of syntactic parallelism and semantic opposition. It is a separate detection problem. This research found no evaluated method that can be adopted directly for this repository.

## Useful text statistics

The following metrics are proposals, with no calibrated thresholds:

| Metric | Definition | Purpose |
|--------|------------|---------|
| Event density | `1000 * contrast_events / prose_words` | Compare contrast use in similar documents |
| Sentence coverage | `100 * affected_sentences / prose_sentences` | Show how much of the prose uses these frames |
| Family counts | Separate corrective, additive, concessive, and tail counts | Avoid collapsing different functions |
| Local concentration | Event counts per paragraph or fixed-size window | Locate repetitive framing |
| Frame repetition | Counts of repeated normalized construction types | Separate repeated templates from isolated contrasts |

Count each distinct occurrence. Deduplicate overlapping regex and dependency matches of the **same event**, not repeated uses elsewhere in the document. Repeated occurrences are the signal being measured. A cross-sentence event counts once; both sentences may contribute to sentence coverage. Report raw counts and denominators alongside rates, with undefined rates represented explicitly for empty input.

TTR, burstiness, readability, and generic POS repetition can describe other style properties. They cannot establish that X has been superseded. Short documents have unstable rates; document length and genre must be controlled when comparing samples.

Evaluation needs separate labels for construction type and editorial action: retain, simplify, or remove the rejected alternative. Measure detection precision and recall by family. For the lasso/net problem, evaluate paired conversations and resulting drafts, including cases where the final text legitimately explains a correction.

No matched-corpus study establishing that these particular constructions are overrepresented in LLM output was found in this research. They are style-review signals, not evidence of AI authorship.

## How and when LLMs produce it

**Reported context:** An OpenAI community user describes recurring "not this, but that" framing during long-form Arabic editing and rewriting, across topics and tones. This is one anecdotal account, without a reproducible model transcript or frequency measurement. [User report](https://community.openai.com/t/most-annoying-habit-can-i-make-it-stop/1265708)

**Indirect experimental evidence:** Mann et al.'s preprint measures forbidden-concept token probabilities after "do not mention X" instructions with intervening distractors. The authors report rebound effects that depend on distractor length and type. This tests concept suppression. It does not measure correction carryover or explain the lasso/net failure. [Study, abstract and methods](https://arxiv.org/html/2511.12381)

**Exact failure:** This research found no controlled measurement of corrections carried into final deliverables. The user's example identifies topic revision as one context; the existing Compliance Narration example identifies explaining an instruction's exclusions as another. Neither example measures frequency.

**Working explanation:** The assistant may explain the correction to show compliance and keep X as a rhetorical foil for Y. This is an untested task-level hypothesis. The underlying model mechanism remains unknown.

The skill's response is to update the accepted subject before drafting. Keep an earlier alternative only when it informs the finished text's reader.

## Recommended changes, in priority order

1. **Clarify the skill's editorial rule.** Add the lasso/net example to the existing Binary Contrasts and Compliance Narration guidance. Update the accepted subject before drafting. Preserve safety limits, requested comparisons, and explanations of a reader-relevant misconception.
2. **Separate detection from deletion advice.** Report a contrast candidate and its family. Ask whether the rejected alternative contributes information. Additive frames must retain both positive claims if rewritten.
3. **Broaden candidate coverage and improve disambiguation.** Extend token rules, reuse existing spaCy tokens, and add a bounded adjacent-sentence pass. Keep the canonical corrective, additive, concessive, and factual-negative controls distinct.
4. **Report event counts and rates.** Deduplicate by event span, with retained paragraph and sentence boundaries. Preserve current JSON fields and the existing sentence-index meaning of `findings[].line`.
5. **Consider conversation-aware review separately.** In the skill, the assistant already has the conversation. A standalone detector would need an explicit context input or rejected/accepted concept pairs. Match resurfacing rejected concepts, then assess audience relevance before recommending their removal.

The conversation-aware option can begin with lexical or lemma matching. Paraphrases may need semantic matching, which adds its own false positives. Presence of a rejected concept is still insufficient: a document about the correction itself may need it.

The detector extensions and metrics above are proposals. The strongest immediate intervention for the user's example is the skill-level instruction to remove superseded framing.
