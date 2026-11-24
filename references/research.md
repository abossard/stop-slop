# Research

The skill implements one study: Clark, Martin & Mahowald, "Why is AI-generated language so hard to understand?", [arXiv:2610.29162](https://arxiv.org/abs/2610.29162), 21 October 2026. It is a preprint.

## What the study did

- It collected text from 14 models. Nine are frontier or near-frontier: Claude Sonnet 5, Opus 5, Opus 5.5 and Fable 5, GPT-5.6 Luna, Terra and Sol, GLM-5 and Kimi K2.5. Five are small open models: Llama 3.1 8B (base, Instruct) and Olmo 3 7B (base, Instruct, Think).
- It used three settings: 120 chat conversations of 12 turns, 45 coding sessions on five GitHub repositories, and 980 essays on seven school assignments.
- It counted six kinds of construction that earlier reading studies tie to slower reading. [Constructions](constructions.md) lists them with those studies.
- It compared each model with human text of the same kind. That text was film subtitles for chat, StackExchange posts for coding, and 2,934 student essays.
- It also compared each model sentence with a paraphrase of itself, made by translating the sentence to Japanese and back. A construction that disappears in the paraphrase is one that the model chose over another way to say the same thing.

## What it found

| Finding | Basis |
|---------|-------|
| All nine frontier and near-frontier models use human verbs on things, and rare sequences of words, more often than human text does | measured in every setting |
| Most of them also use longer dependencies, more noun stacks and more object relative clauses without "that" | measured, most models |
| Frontier models use four constructions more often than paraphrases of their own text do: rare sequences of words, nouns used as verbs, human verbs on things and clauses without "that". They use clauses with "that" less often | measured |
| The over-use is smaller in single-prompt essays than in multi-turn chat and coding | measured. The authors guess that long sessions push a model to compress |
| Models differ. Paraphrasing changes the Llama models and the base Olmo model least. Opus 5.5 is lower than Opus 5 on 19 of 21 comparisons | measured |
| A 1.5B model that is fine-tuned with a length penalty moves to the shorter of two equivalent phrasings. Without KL regularization it drops an optional "that" over 98% of the time, and it also drops "that" in constructions it never saw in training | proof of concept on one small model |
| Training on verifiable rewards causes the compression in frontier models | hypothesis |

## What it did not show

- It did not test readers on model text. Each construction's link to reading difficulty comes from the earlier studies.
- It did not test whether instructions to a model reduce the constructions. This skill is such an instruction.
- It covers English only, with 15 conversation seeds.

## What the skill adds on its own

- Step 1 of "Before you write" (choose the points first, then write each one in full) is our reading of the length-penalty experiment: pressure on the number of words compresses sentences, so the skill puts the pressure on the number of points.
- The translator check in "After you write" turns the study's paraphrase method into a check for the writer. The study did not test it as one.

## How readcheck differs from the study's method

| Study | `tools/readcheck` |
|-------|-------------------|
| Parses with spaCy `en_core_web_trf` | Parses with `en_core_web_sm`, which makes more parsing mistakes |
| Noun stacks: three or more nouns in a modifier relation | The same, counting common nouns only and a hyphenated pair as one |
| Object relative clauses, with and without a relativizer | The same. It flags only a clause that has a noun subject and no "that" |
| Dependency length, standardized over five sentence-length bins with weights from Wikipedia | The same bins, with weights from the Brown corpus (1.05M words). Brown itself scores 2.24 words |
| Human verbs on things: parser candidates that a classifier judges | A fixed list of human verbs, which finds fewer cases |
| Nouns used as verbs: parser candidates that a classifier judges | Not measured |
| Unattested word pairs and trigram perplexity against a reference corpus | Not measured |

## Not measured

Nobody has measured whether this skill reduces the constructions, or whether people read its output faster. Such a measurement needs a lot of text, because each construction occurs only a few times per 1,000 words. It also needs long sessions, where the study found the largest effects.
