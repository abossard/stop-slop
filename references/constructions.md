# Constructions that slow a reader

Six constructions that frontier models use more often than people do. Each example is model output quoted in Clark, Martin & Mahowald (2026, [arXiv:2610.29162](https://arxiv.org/abs/2610.29162)), with the model and the setting. The rewrites are ours. Sources and limits are in [research](research.md).

## 1. Unusual word pairs

Two words in a row that people rarely put together. Often the pair is a label or a compound that the model coined.

A reader predicts the next word, and reading time grows as a word gets harder to predict (Levy 2008; Smith & Levy 2013). All nine frontier and near-frontier models used rare sequences of words more often than human text does.

| Instead of | Write |
|------------|-------|
| "Every behavioral test was verified red against the original source" (Opus 5, coding; the phrase came back four times in one conversation) | "I checked that every behavioral test fails on the original code" |
| "it's the part most internet advice glosses over" (Fable 5, chat) | "most advice on the internet skips this part" |
| "the existing xfailed lazy-intermediate Lookup behavior" (GPT-5.6 Terra, coding) | Name the test and say in a clause what it does. |

Use the phrase that people already say for the thing. When no such phrase exists, spend a clause on it. `readcheck` does not measure this: it needs a large reference corpus.

## 2. Human verbs on things

An active verb that normally takes a person or an animal, with a thing as its subject.

Readers use the subject to predict what kind of verb comes next. A subject that does not fit its verb makes them read the sentence again (Trueswell et al. 1994; Kim & Osterhout 2005; Kuperberg 2007). All nine frontier and near-frontier models did this more often than human text.

| Instead of | Write |
|------------|-------|
| "`is_file()` swallows that and returns False" | "`is_file()` ignores that error and returns False" |
| "Puzzle patterns where this asymmetry bites" | "Puzzle patterns where this asymmetry causes a problem" |
| "The docstring promises they're skipped" (Fable 5, coding) | "The docstring says that they are skipped" |
| "an existing check that covered str but forgot its sibling scalar-like type bytes" (Sonnet 5, coding) | "an existing check that covered `str` but not `bytes`, the other scalar-like type" |
| "the time objection misunderstands how service actually functions" (Kimi K2.5, essay) | "people who object that service takes time misunderstand how it works" |

Give the thing the plain verb for what it does (reads, returns, rejects, drops, causes, shows), or make a person the subject. `readcheck` flags a fixed list of human verbs, so it finds only some cases.

## 3. Words that belong together, far apart

A subject far from its verb, or a verb far from its object.

The reader holds the first word in memory until the second one arrives (Gibson 1998, 2000; Grodner & Gibson 2005). Speakers of 37 languages keep these distances short (Futrell et al. 2015). Most frontier models wrote longer distances than human text.

| Instead of | Write |
|------------|-------|
| "A cat who can always get up and away is a much calmer cat." (Opus 5, chat) | "A cat is much calmer when it can always get up and away." |
| "A lattice constructed with duplicate points, or a SymbolSet with colliding labels/names, can overwrite internal dictionary or attribute mappings." (GPT-5.6 Terra, coding) | "Two things can overwrite internal dictionary or attribute mappings: a lattice constructed with duplicate points, and a SymbolSet with colliding labels or names." |

Put the verb next to its subject and the object next to its verb. Move a long condition or a list to the end of the sentence, or give it a sentence of its own. `readcheck` flags a subject or object that is 10 or more words from its verb, and reports the mean distance as `dependency_length`.

## 4. Noun stacks

Three or more nouns in a row, where each one modifies a later one.

The reader has to work out which noun belongs to which, as in the headline "Squad Helps Dog Bite Victim". New compounds disrupt reading (Staub et al. 2007; Cohen & Staub 2014). Most frontier models stacked more nouns than human text.

| Instead of | Write |
|------------|-------|
| "a community service honor cord at graduation" (Fable 5, essay) | "an honor cord for community service at graduation" |
| "a horror movie soundtrack generator" (Sonnet 5, chat) | "a generator of horror-movie soundtracks" |
| "Fixed absolute dotfile backup path handling" (GPT-5.6 Luna, coding) | Say which path is absolute, the path of the dotfile or the path of the backup. The stack does not tell the reader. |

Say how the nouns relate, with "of", "for" or a clause. Two nouns in a row are normal. `readcheck` flags three or more common nouns in one chain and does not count proper nouns.

## 5. Clauses without "that"

An object relative clause with no "that" or "which" in front of it.

Object relative clauses are harder than subject relative clauses (Staub 2010). The gap is smaller for frequent forms, such as a clause with a pronoun as its subject (Reali & Christiansen 2007). Speakers add an optional "that" where the next words are hard to predict (Levy & Jaeger 2007; Jaeger 2010). Frontier models used the form without "that" more often than paraphrases of their own text, and the form with "that" less often.

| Instead of | Write |
|------------|-------|
| "the others check behaviour the old code never reached" (Opus 5.5, coding) | "the others check behaviour that the old code never reached" |
| "the exact skills the worksheet hoped to teach" (Opus 5.5, essay) | "the exact skills that the worksheet was meant to teach" |

Add "that" when the clause has a noun as its subject. With a pronoun the short form reads fine: "activities they care about". The same goes for the other optional words in the study's training experiment: "knew (that)", "sure (that)", "so (that)". Keep them when the words that follow are long or new to the reader. `readcheck` counts every object relative clause. It flags a clause that has a noun as its subject and no "that".

## 6. Nouns used as verbs

A word that people use as a noun, used as a verb for the occasion.

Changing a word's part of speech makes the reader re-evaluate the sentence (Thierry et al. 2008). Frontier models did this more often than paraphrases of their own text.

| Instead of | Write |
|------------|-------|
| "calendar it" (Fable 5, chat) | "put it in your calendar" |

Verbs that started as nouns and are now ordinary are fine: "filter", "bottle", "mirror". `readcheck` does not measure this. The study uses a classifier for it.
