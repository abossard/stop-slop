#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "textstat>=0.7.0",
#   "spacy>=3.7.0,<3.9",
#   "lexicalrichness>=0.5.0",
#   "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl",
# ]
# ///
"""AI slop detector — analyzes text for common AI-generated writing patterns.

Metrics:
  - Burstiness: sentence length variance (low = AI-like uniformity)
  - Lexical diversity: type-token ratio (low = repetitive vocabulary)
  - AI vocabulary density: Kobak et al. frequency-ratio words per 1000 words
  - Passive voice rate: fraction of sentences with passive constructions
  - Readability: Flesch-Kincaid grade level via textstat

Usage:
  echo "your text" | python analyze.py           # human-readable
  echo "your text" | python analyze.py --json     # machine-readable
  python analyze.py --file input.txt --json       # from file
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys

# --- Optional heavy dependencies with graceful degradation ---

try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False

try:
    import spacy
    try:
        _nlp = spacy.load("en_core_web_sm")
    except OSError:
        _nlp = None
    HAS_SPACY = _nlp is not None
except ImportError:
    _nlp = None
    HAS_SPACY = False

try:
    from lexicalrichness import LexicalRichness
    HAS_LEXRICH = True
except ImportError:
    HAS_LEXRICH = False


# --- AI vocabulary list (Kobak et al. 2025, arXiv:2406.07016) ---

# --- AI vocabulary tiers ---
# Tier 1 (high-signal): words with frequency ratio ≥5× in AI text.
# These are strong standalone signals. Source: Kobak et al. 2025.
AI_TIER1_VERBS = {
    "delve", "underscore", "showcase", "elucidate", "navigate",
    "foster", "leverage", "harness", "illuminate", "spearhead",
    "bolster", "streamline", "encompass", "revolutionize", "embark",
}

AI_TIER1_ADJECTIVES = {
    "multifaceted", "pivotal", "nuanced", "holistic", "transformative",
    "groundbreaking", "cutting-edge", "invaluable",
    "meticulous", "intricate",
}

AI_TIER1_NOUNS = {
    "tapestry", "landscape", "paradigm", "synergy", "ecosystem",
    "realm", "cornerstone", "testament", "beacon", "catalyst",
    "underpinning", "interplay",
}

# Tier 2 (medium-signal): common words that spike in AI text but also appear
# in normal technical writing. Only flagged when co-occurring with other signals.
# Source: Kobak et al. 2025 "common 10" set (Δcommon=0.134) + corroborated words.
# Extended with the broad list from Wikipedia:Signs_of_AI_writing. Those words
# ("robust", "key", "valuable") are frequent in legitimate technical prose, so
# they stay in tier 2 rather than tier 1.
AI_TIER2_WORDS = {
    "comprehensive", "crucial", "enhancing", "exhibited", "insights",
    "commendable", "notable", "paramount",
    "robust", "valuable", "vibrant", "enduring", "garner", "boast",
    "align", "emphasize", "enhance", "highlight", "key", "profound",
    "renowned", "exemplify", "seamless",
    "decisive", "decisively", "decisiveness",
}

AI_TRANSITIONS = {
    "furthermore", "moreover", "notably", "consequently",
    "additionally",
}

# Kobak "common 10" — words whose aggregate frequency strongly predicts LLM use.
# Not flagged individually (too common), but their density is tracked separately.
KOBAK_COMMON_10 = {
    "across", "additionally", "comprehensive", "crucial", "enhancing",
    "exhibited", "insights", "notably", "particularly", "within",
}

AI_PHRASES = [
    "it is worth noting", "it is important to note", "in the context of",
    "plays a crucial role", "sheds light on", "paves the way",
    "remains a significant challenge", "has garnered significant attention",
    "offers a promising avenue", "it is imperative to",
    "a comprehensive understanding", "in light of the above",
    "warrants further investigation", "a growing body of",
    "in conclusion", "this underscores", "this study aims to",
    "the findings suggest", "this highlights the",
    "it is essential to", "it is crucial to",
    "a wide range of", "a broad range of",
    "plays a vital role", "plays a significant role",
    "plays a key role", "plays a pivotal role",
]

# High-signal words used for primary AI vocab density (backward-compatible)
ALL_AI_WORDS = AI_TIER1_VERBS | AI_TIER1_ADJECTIVES | AI_TIER1_NOUNS | AI_TRANSITIONS

# One compiled alternation instead of one scan per phrase. Longest-first so an
# overlapping pair resolves to the more specific phrase.
AI_PHRASE_RE = re.compile(
    "|".join(re.escape(p) for p in sorted(AI_PHRASES, key=len, reverse=True))
)

# Sentence starters typical of AI text (Przystalski et al. 2025; multi_detector.py)
AI_SENTENCE_STARTERS = [
    "furthermore,", "moreover,", "additionally,", "consequently,",
    "in conclusion,", "it is worth noting", "it is important to note",
    "in today's", "in the modern", "in an era",
    "this highlights", "this underscores", "this showcases",
    "notably,", "specifically,", "crucially,", "importantly,",
]

# --- Model-era signature markers ---
# Rare but highly diagnostic tics. Measured at 19.5 hits per 100k words on
# Opus 5 (~0.2/1000), far below the >10/1000 AI-vocabulary density flag, so
# these are counted by occurrence instead of density.
# Sources: github.com/anthropics/claude-code/issues/53454,
# reddit.com/r/ClaudeAI/comments/1tob6q5, jola.dev "how to stop Claude from
# saying load-bearing".
_APO = "[\u2019']"

SIGNATURE_MARKERS = {
    "load-bearing": r"\bload[-\s]bearing\b",
    "honest take": rf"\bhonest\s+(?:take|truth)\b",
    "not nothing": r"\bnot nothing\b",
    "sit with that": r"\bsit with (?:that|it|this)\b",
    "doing a lot of work": r"\bdoing a lot of (?:the )?work\b",
    # Only the abstract/metaphorical use. A bare `seam` match fires on coal
    # seams, weld seams, sewing seams and seam carving, which are ordinary
    # domain nouns, so the collocation is required.
    "seam": r"\b(?:load[-\s]bearing|structural|conceptual|architectural)\s+seams?\b"
            r"|\bseams?\s+(?:of|in)\s+the\s+(?:argument|design|abstraction|reasoning)\b",
}

SIGNATURE_MARKER_RES = {
    label: re.compile(pattern, re.IGNORECASE)
    for label, pattern in SIGNATURE_MARKERS.items()
}

# Negation-then-correction frames. Restricted to copular constructions so
# ordinary negation ("I did not fix it") is not swept up.
# Corroborated by Wikipedia:Signs_of_AI_writing ("parallel constructions
# involving not, but, or however") and Hollis Robbins ("it's not just X, but Y").
NEGATIVE_PARALLELISM_RES = [
    re.compile(rf"\bnot just\b[^.!?]*?\b(?:but|it{_APO}?s)\b", re.IGNORECASE),
    re.compile(r"\bnot only\b[^.!?]*?\bbut\b", re.IGNORECASE),
    re.compile(
        rf"\b(?:is|was|are|were|it{_APO}s|that{_APO}s|there{_APO}s)\s+not\b"
        rf"[^.!?]*?,\s*(?:it|that|they|there){_APO}?s\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\b(?:is|are|was|were|does|did|do)n{_APO}t\b"
        rf"[^.!?]*?,\s*(?:it|that|they){_APO}?s\b",
        re.IGNORECASE,
    ),
    re.compile(rf"\bthat{_APO}?s not nothing\b", re.IGNORECASE),
    # "but" must introduce an alternative predicate, not a new clause.
    # Excluding a following subject pronoun keeps concessive uses out:
    # "The build is not reproducible but we ship it anyway."
    re.compile(
        r"\b(?:is|was|are|were)\s+not\s+(?:a|an|the)?\s*[^.!?,]*?\bbut\s+"
        r"(?!we\b|i\b|they\b|he\b|she\b|you\b|it\b|that\b|this\b|there\b)",
        re.IGNORECASE,
    ),
]

# Validation openers. Sycophancy is a documented RLHF artifact: preference
# models favour responses matching the user's view (arXiv:2310.13548).
SYCOPHANCY_RES = [
    re.compile(
        rf"^you(?:{_APO}re|\s+are)\s+"
        r"(?:absolutely|completely|totally|so|entirely)\s+right",
        re.IGNORECASE,
    ),
    # Restricted to speech-act verbs. A bare `right to \w+` also matches
    # "You're right to left of the divider".
    re.compile(
        rf"^you(?:{_APO}re|\s+are)\s+right\s+to\s+"
        r"(?:call|point|push|question|flag|raise|challenge|note|highlight)\b",
        re.IGNORECASE,
    ),
    re.compile(r"^(?:great|excellent|good|fair|sharp)\s+(?:question|point|catch)",
               re.IGNORECASE),
    re.compile(
        rf"^(?:that|this){_APO}?s\s+(?:a\s+)?(?:sharp|great|excellent|really good)\s+"
        r"(?:insight|point|question|catch|observation)",
        re.IGNORECASE,
    ),
]

# Leading markdown decoration, stripped before the sentence-start anchors run.
# The consuming skill lints markdown, where "- You're absolutely right" and
# "**You're absolutely right**" are common.
MARKDOWN_PREFIX_RE = re.compile(r"^(?:[>\-*+#]+\s*|\d+[.)]\s*|[*_`]{1,3})+")

# Metadiscourse preamble before the actual content. Hyland's (2005) frame
# markers and code glosses; LLM text is skewed toward interactive metadiscourse
# (Jiang & Hyland, ESP 2025).
THROAT_CLEARING_RES = [
    re.compile(r"\blet me be (?:honest|clear|direct|blunt)\b", re.IGNORECASE),
    re.compile(r"\bi need to be (?:\w+\s+)?honest\b", re.IGNORECASE),
    # The discourse-marker use is punctuated. Without the trailing comma or
    # colon this also matches "clear-headed", "to be fair to him", and
    # "designed to be fair", which are ordinary prose.
    re.compile(r"\bto be (?:clear|honest|fair|blunt)\s*[,:]", re.IGNORECASE),
    re.compile(rf"\bhere{_APO}s the thing\b", re.IGNORECASE),
    re.compile(rf"\blet{_APO}s unpack\b", re.IGNORECASE),
    re.compile(rf"\bi{_APO}ll be honest\b", re.IGNORECASE),
    re.compile(r"\bi will give it to you straight\b", re.IGNORECASE),
]

# Importance-inflation frames built on "decisive"/"decisively".
# Wikipedia:Signs_of_AI_writing documents the move — "a crucial/pivotal/vital
# role/moment", "key turning point" — where an arbitrary fact is upgraded into
# a turning point. "decisive" performs the same upgrade for causation and is
# absent from the Kobak et al. excess-vocabulary list, so it gets no density
# treatment: the bare adjective is ordinary in military, sports and election
# prose ("a decisive victory", "she is decisive under pressure"). Only the
# verdict, role, turning-point and call-to-action collocations are matched.
DECISIVENESS_RES = [
    re.compile(r"\b(?:prove[sd]?|proven|proving)\s+(?:to be\s+)?decisive\b",
               re.IGNORECASE),
    re.compile(r"\b(?:is|are|was|were)\s+decisive\s+in\b", re.IGNORECASE),
    re.compile(r"\bplay(?:s|ed|ing)?\s+(?:a|the)\s+decisive\s+role\b",
               re.IGNORECASE),
    re.compile(
        r"\b(?:a|the|this|that|its)\s+decisive\s+"
        r"(?:factor|moment|shift|step|turning\s+point|advantage|edge|break)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bdecisive\s+action\b", re.IGNORECASE),
    re.compile(
        r"\b(?:acts?|acted|acting|moves?|moved|moving|responds?|responded|"
        r"responding|intervenes?|intervened|intervening|leads?|led|leading)"
        r"\s+decisively\b",
        re.IGNORECASE,
    ),
]

EM_DASH = "\u2014"

# Minimum POS tokens before syntactic-template rates are stable enough to
# report. Matches the conservative floors used for hapax/Yule's K/MTLD.
TEMPLATE_MIN_TOKENS = 100


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using regex. Handles abbreviations reasonably."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _word_tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer."""
    return re.findall(r"[a-z]+(?:[-'][a-z]+)*", text.lower())


def _compute_burstiness(sentence_lengths: list[int]) -> float:
    """Burstiness = stdev / mean of sentence word counts. 0 if ≤1 sentence."""
    if len(sentence_lengths) < 2:
        return 0.0
    mean = statistics.mean(sentence_lengths)
    if mean == 0:
        return 0.0
    stdev = statistics.stdev(sentence_lengths)
    return round(stdev / mean, 4)


def _compute_ttr(words: list[str]) -> float:
    """Type-token ratio = unique words / total words."""
    if not words:
        return 0.0
    return round(len(set(words)) / len(words), 4)


def _lemmatize_fallback(word: str, lexicon: set[str]) -> str:
    """Lemmatize via simple suffix stripping (no spaCy)."""
    if word.endswith("ing") and len(word) > 5:
        base = word[:-3]
        if base + "e" in lexicon:
            return base + "e"
        if base in lexicon:
            return base
    if word.endswith("es") and len(word) > 4:
        if word[:-2] in lexicon:
            return word[:-2]
        if word[:-1] in lexicon:
            return word[:-1]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        if word[:-1] in lexicon:
            return word[:-1]
    if word.endswith("ed") and len(word) > 4:
        if word[:-2] in lexicon:
            return word[:-2]
        if word[:-1] in lexicon:
            return word[:-1]
        if word[:-2] + "e" in lexicon:
            return word[:-2] + "e"
    return word


def _spacy_analyze(text: str) -> dict:
    """Single spaCy pass over the full text. Returns lemma map, passive sentence texts, POS tags."""
    if not HAS_SPACY:
        return {"lemmas": {}, "passive_sentence_texts": set(), "pos_tags": []}

    doc = _nlp(text)
    # Build token -> lemma mapping
    lemmas = {}
    for tok in doc:
        lower = tok.text.lower()
        if lower not in lemmas:
            lemmas[lower] = tok.lemma_.lower()

    # Collect text of passive sentences (normalized for matching)
    passive_sentence_texts = set()
    for sent in doc.sents:
        if any(tok.dep_ in ("nsubjpass", "auxpass") for tok in sent):
            passive_sentence_texts.add(sent.text.strip())

    pos_tags = [tok.pos_ for tok in doc if not tok.is_space]

    return {
        "lemmas": lemmas,
        "passive_sentence_texts": passive_sentence_texts,
        "pos_tags": pos_tags,
    }


def _lexicon_hit(word: str, spacy_lemmas: dict, lexicon: set[str]) -> bool:
    """True if the word belongs to the lexicon by surface form, spaCy lemma,
    or suffix fallback.

    spaCy mis-tags inflections in some contexts: in "The comprehensive review
    delves into crucial insights.", it reads "delves" as a noun and lemmatizes
    it to "delf", which silently drops a tier-1 word. A lexicon miss therefore
    retries with suffix stripping instead of trusting the tagger alone.
    """
    if word in lexicon:
        return True
    if spacy_lemmas.get(word) in lexicon:
        return True
    return _lemmatize_fallback(word, lexicon) in lexicon


def _compute_ai_vocab_density(words: list[str], spacy_lemmas: dict) -> float:
    """Count AI vocabulary words per 1000 words. Lemmatizes to catch inflections."""
    if not words:
        return 0.0
    hits = sum(1 for w in words if _lexicon_hit(w, spacy_lemmas, ALL_AI_WORDS))
    hits += len(AI_PHRASE_RE.findall(" ".join(words)))
    return round(hits / len(words) * 1000, 2)


def _compute_hapax_ratio(words: list[str]) -> float | None:
    """Hapax legomena ratio = words appearing exactly once / unique words.
    AI: 0.45-0.60, Human: 0.60-0.85 (Opara 2024, top-4 feature).
    Returns None if fewer than 50 words (unstable on short text)."""
    if len(words) < 50:
        return None
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    unique = len(freq)
    if unique == 0:
        return 0.0
    hapax = sum(1 for c in freq.values() if c == 1)
    return round(hapax / unique, 4)


def _compute_yules_k(words: list[str]) -> float | None:
    """Yule's K = 10⁴ × (M₂ − N) / N² where N=total words, M₂=Σ(fᵢ²).
    Higher K = more repetitive = more AI-like.
    AI: 80-200, Human: 20-100 (multi_detector.py, Retengart/entropy-analysis).
    Returns None if fewer than 50 words."""
    if len(words) < 50:
        return None
    n = len(words)
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    m2 = sum(f * f for f in freq.values())
    if n * n == 0:
        return 0.0
    return round(10000 * (m2 - n) / (n * n), 2)


def _compute_contraction_rate(text: str, sentences: list[str]) -> float:
    """Contractions per sentence. AI uses fewer contractions (Opara 2024).
    Measures formality; not a standalone AI marker."""
    if not sentences:
        return 0.0
    contraction_re = re.compile(
        r"\b\w+(?:'(?:t|s|re|ve|ll|d|m))\b", re.IGNORECASE
    )
    count = len(contraction_re.findall(text))
    return round(count / len(sentences), 4)


def _detect_ai_starters(sentences: list[str]) -> list[dict]:
    """Detect sentences that begin with AI-typical transition starters.
    Source: Przystalski et al. 2025, multi_detector.py."""
    findings = []
    for idx, sent in enumerate(sentences):
        sent_lower = sent.lower().lstrip()
        for starter in AI_SENTENCE_STARTERS:
            if sent_lower.startswith(starter):
                findings.append({
                    "line": idx + 1,
                    "starter": starter.rstrip(","),
                })
                break
    return findings


def _detect_signature_markers(text: str) -> dict[str, int]:
    """Count model-era signature markers by occurrence.

    Density is the wrong instrument here: 'load-bearing' is reported at
    19.5 hits per 100k words on Opus 5, roughly 0.2 per 1000 words, so it
    would never cross the AI-vocabulary density threshold.
    """
    counts = {}
    for label, pattern in SIGNATURE_MARKER_RES.items():
        hits = len(pattern.findall(text))
        if hits:
            counts[label] = hits
    return counts


def _compute_lexicon_density(
    words: list[str], lexicon: set[str], spacy_lemmas: dict
) -> float:
    """Words from a lexicon per 1000 words, lemmatized to catch inflections."""
    if not words:
        return 0.0
    hits = sum(1 for w in words if _lexicon_hit(w, spacy_lemmas, lexicon))
    return round(hits / len(words) * 1000, 2)


def _compute_syntactic_templates(pos_tags: list[str], has_pos: bool) -> dict | None:
    """POS n-gram template repetition (Shaib et al. 2024, arXiv:2407.00211).

    A template is a POS n-gram that repeats at least twice. The rate is the
    fraction of n-gram positions covered by a repeated n-gram, averaged over
    n in 4..8.

    The rate is NOT length-invariant: it climbs with document size because
    longer texts give every n-gram more chances to recur. Measured on one
    human-written corpus it ran 0.13 at 150 words and 0.61 at 28k words, so
    the number is only comparable between texts of similar length and carries
    no AI-like threshold.

    Returns None with a `reason` when it cannot be computed.
    """
    if not has_pos:
        return None
    if len(pos_tags) < TEMPLATE_MIN_TOKENS:
        return None

    by_n = {}
    top_templates = []
    for n in range(4, 9):
        if len(pos_tags) < n:
            continue
        ngrams = [tuple(pos_tags[i:i + n]) for i in range(len(pos_tags) - n + 1)]
        counts = {}
        for gram in ngrams:
            counts[gram] = counts.get(gram, 0) + 1
        repeated = sum(1 for gram in ngrams if counts[gram] >= 2)
        by_n[n] = round(repeated / len(ngrams), 4)
        if n == 6:
            ranked = sorted(counts.items(), key=lambda kv: -kv[1])
            top_templates = [
                {"pattern": " ".join(gram), "count": count}
                for gram, count in ranked[:3] if count >= 2
            ]

    if not by_n:
        return None

    return {
        "template_rate": round(sum(by_n.values()) / len(by_n), 4),
        "by_n": by_n,
        "top_templates": top_templates,
        "pos_token_count": len(pos_tags),
    }


def _match_labels(sent: str, patterns: list) -> list[str]:
    """Return the matched substrings for every pattern that fires."""
    hits = []
    for pattern in patterns:
        found = pattern.search(sent)
        if found:
            hits.append(found.group(0).strip())
    return hits


def _compute_passive_voice_rate(
    sentences: list[str], passive_texts: set[str] | None = None
) -> float:
    """Fraction of sentences with passive voice."""
    if not sentences:
        return 0.0

    if passive_texts is not None:
        # Match our regex-split sentences against spaCy's passive detections
        count = sum(1 for s in sentences if s.strip() in passive_texts)
        return round(count / len(sentences), 4)

    # Regex fallback
    passive_re = re.compile(
        r'\b(?:was|were|been|being|is|are|am)\s+\w+(?:ed|en|t)\b', re.IGNORECASE
    )
    passive_count = sum(1 for s in sentences if passive_re.search(s))
    return round(passive_count / len(sentences), 4)


def _compute_readability(text: str) -> float:
    """Flesch-Kincaid grade level."""
    if HAS_TEXTSTAT and text.strip():
        return round(textstat.flesch_kincaid_grade(text), 2)
    return 0.0


def _generate_findings(
    sentences: list[str], words: list[str],
    spacy_lemmas: dict, passive_texts: set[str] | None = None,
) -> list[dict]:
    """Per-sentence findings with sentence indices and issues."""
    findings = []

    for idx, sent in enumerate(sentences):
        issues = []
        sent_words = _word_tokenize(sent)

        # Check AI vocabulary (lemmatized to catch inflections)
        ai_words_found = [w for w in sent_words if _lexicon_hit(w, spacy_lemmas, ALL_AI_WORDS)]
        if ai_words_found:
            issues.append(
                f"AI-overused words: {', '.join(ai_words_found)} "
                f"(Kobak et al. frequency ratios)"
            )

        # Check AI phrases
        sent_lower = sent.lower()
        matched_phrases = set(AI_PHRASE_RE.findall(sent_lower))
        for phrase in AI_PHRASES:
            if phrase in matched_phrases:
                issues.append(f"AI-typical phrase: \"{phrase}\"")

        # Check passive voice
        if passive_texts is not None:
            if sent.strip() in passive_texts:
                issues.append("Passive voice — name the actor")
        else:
            passive_re = re.compile(
                r'\b(?:was|were|been|being|is|are)\s+\w+(?:ed|en|t)\b',
                re.IGNORECASE
            )
            if passive_re.search(sent):
                issues.append("Possible passive voice — name the actor")

        # Check hedge stacking (≥2 hedges in one sentence)
        hedge_words = re.findall(
            r'\b(?:may|might|could|possibly|potentially|perhaps|arguably|'
            r'typically|often|generally|tends?\s+to|in\s+some\s+cases)\b',
            sent_lower
        )
        if len(hedge_words) >= 2:
            issues.append(
                f"Hedge stacking: {len(hedge_words)} hedges "
                f"({', '.join(hedge_words)})"
            )

        # Check AI-typical sentence starters (Przystalski et al. 2025)
        sent_stripped = sent_lower.lstrip()
        for starter in AI_SENTENCE_STARTERS:
            if sent_stripped.startswith(starter):
                issues.append(
                    f"AI-typical starter: \"{starter.rstrip(',')}\""
                )
                break

        # Model-era signature markers (occurrence-based, not density-based)
        for label, pattern in SIGNATURE_MARKER_RES.items():
            if pattern.search(sent):
                issues.append(
                    f"Signature LLM marker: \"{label}\" "
                    f"(claude-code#53454 frequency data)"
                )

        # Negation-then-correction frames
        for hit in _match_labels(sent, NEGATIVE_PARALLELISM_RES):
            issues.append(f"Negative parallelism: \"{hit}\" — state the positive claim")
            break

        # Validation openers (RLHF sycophancy artifact, arXiv:2310.13548).
        # Markdown decoration is stripped so list items and bold text still
        # hit the sentence-start anchors.
        sent_anchor = MARKDOWN_PREFIX_RE.sub("", sent_stripped)
        for hit in _match_labels(sent_anchor, SYCOPHANCY_RES):
            issues.append(f"Sycophantic opener: \"{hit}\" — cut it and answer")
            break

        # Metadiscourse preamble (Hyland frame markers)
        for hit in _match_labels(sent, THROAT_CLEARING_RES):
            issues.append(f"Throat-clearing: \"{hit}\" — state the point directly")
            break

        # Importance inflation via "decisive" (Wikipedia:Signs_of_AI_writing)
        for hit in _match_labels(sent, DECISIVENESS_RES):
            issues.append(
                f"Importance inflation: \"{hit}\" — name what actually changed"
            )
            break

        # Tier-2 words are too common to flag alone; only when clustered
        # with another signal in the same sentence.
        if issues:
            tier2_found = [
                w for w in sent_words
                if _lexicon_hit(w, spacy_lemmas, AI_TIER2_WORDS)
            ]
            if tier2_found:
                issues.append(
                    f"Tier-2 AI words clustered with other signals: "
                    f"{', '.join(sorted(set(tier2_found)))}"
                )

        if issues:
            findings.append({
                "line": idx + 1,
                "sentence": sent[:120] + ("..." if len(sent) > 120 else ""),
                "issues": issues,
            })

    return findings


def analyze_text(text: str) -> dict:
    """Analyze text and return a metrics dictionary."""
    text = text.strip()
    if not text:
        return {
            "word_count": 0,
            "sentence_count": 0,
            "burstiness": 0,
            "ttr": 0,
            "ai_vocabulary_density": 0,
            "passive_voice_rate": 0,
            "flesch_kincaid_grade": 0,
            "hapax_ratio": None,
            "yules_k": None,
            "contraction_rate": 0,
            "signature_markers": {},
            "tier2_density": 0,
            "kobak_common10_density": 0,
            "em_dash_count": 0,
            "syntactic_templates": None,
            "syntactic_templates_unavailable_reason": None,
            "mtld": None,
            "findings": [],
        }

    sentences = _split_sentences(text)
    words = _word_tokenize(text)
    sentence_lengths = [len(_word_tokenize(s)) for s in sentences]

    # Single spaCy pass for lemmas + passive voice
    spacy_data = _spacy_analyze(text)
    spacy_lemmas = spacy_data["lemmas"]
    passive_texts = spacy_data["passive_sentence_texts"] if HAS_SPACY else None

    result = {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "burstiness": _compute_burstiness(sentence_lengths),
        "ttr": _compute_ttr(words),
        "ai_vocabulary_density": _compute_ai_vocab_density(words, spacy_lemmas),
        "passive_voice_rate": _compute_passive_voice_rate(sentences, passive_texts),
        "flesch_kincaid_grade": _compute_readability(text),
        "hapax_ratio": _compute_hapax_ratio(words),
        "yules_k": _compute_yules_k(words),
        "contraction_rate": _compute_contraction_rate(text, sentences),
        "signature_markers": _detect_signature_markers(text),
        "tier2_density": _compute_lexicon_density(words, AI_TIER2_WORDS, spacy_lemmas),
        "kobak_common10_density": _compute_lexicon_density(
            words, KOBAK_COMMON_10, spacy_lemmas
        ),
        "em_dash_count": text.count(EM_DASH),
        "syntactic_templates": _compute_syntactic_templates(
            spacy_data["pos_tags"], HAS_SPACY
        ),
        "syntactic_templates_unavailable_reason": (
            None if HAS_SPACY else "spacy-unavailable"
        ),
        "sentence_length_mean": round(statistics.mean(sentence_lengths), 2) if sentence_lengths else 0,
        "sentence_length_stdev": round(statistics.stdev(sentence_lengths), 2) if len(sentence_lengths) >= 2 else 0,
        "sentence_length_min": min(sentence_lengths) if sentence_lengths else 0,
        "sentence_length_max": max(sentence_lengths) if sentence_lengths else 0,
        "findings": _generate_findings(sentences, words, spacy_lemmas, passive_texts),
    }

    # MTLD via lexicalrichness (requires enough words for stable measurement)
    if HAS_LEXRICH and len(words) >= 50:
        try:
            lr = LexicalRichness(text)
            result["mtld"] = round(lr.mtld(threshold=0.72), 2)
        except Exception:
            result["mtld"] = None
    else:
        result["mtld"] = None

    return result


def _format_human(result: dict) -> str:
    """Format results for human reading."""
    lines = []
    lines.append("═══ AI Slop Analysis ═══\n")

    lines.append(f"Words: {result['word_count']}  |  Sentences: {result['sentence_count']}")
    lines.append("")

    # Metrics with thresholds
    b = result["burstiness"]
    b_flag = " ⚠ AI-like (uniform sentence lengths)" if b < 0.3 and result["sentence_count"] > 2 else ""
    lines.append(f"Burstiness:          {b:.3f}{b_flag}")

    ttr = result["ttr"]
    ttr_flag = " ⚠ AI-like (repetitive vocabulary)" if ttr < 0.4 and result["word_count"] > 20 else ""
    lines.append(f"TTR:                 {ttr:.3f}{ttr_flag}")

    density = result["ai_vocabulary_density"]
    d_flag = " ⚠ High AI vocabulary density" if density > 10 else ""
    lines.append(f"AI vocab density:    {density:.1f}/1000 words{d_flag}")

    pvr = result["passive_voice_rate"]
    pvr_flag = " ⚠ High passive voice rate" if pvr > 0.2 else ""
    lines.append(f"Passive voice rate:  {pvr:.1%}{pvr_flag}")

    fk = result["flesch_kincaid_grade"]
    lines.append(f"Flesch-Kincaid:      {fk:.1f}")

    mtld = result.get("mtld")
    if mtld is not None:
        mtld_flag = " ⚠ AI-like (low lexical diversity)" if mtld < 50 else ""
        lines.append(f"MTLD:                {mtld:.1f}{mtld_flag}")

    hapax = result.get("hapax_ratio")
    if hapax is not None:
        hapax_flag = " ⚠ AI-like (low hapax ratio)" if hapax < 0.58 else ""
        lines.append(f"Hapax ratio:         {hapax:.3f}{hapax_flag}")

    yules = result.get("yules_k")
    if yules is not None:
        yules_flag = " ⚠ AI-like (high vocabulary repetition)" if yules > 100 else ""
        lines.append(f"Yule's K:            {yules:.1f}{yules_flag}")

    cr = result.get("contraction_rate", 0)
    cr_note = " (formal/AI-like)" if cr == 0 and result["sentence_count"] > 3 else ""
    lines.append(f"Contraction rate:    {cr:.2f}/sentence{cr_note}")

    t2 = result.get("tier2_density", 0)
    lines.append(f"Tier-2 density:      {t2:.1f}/1000 words (flagged only in clusters)")

    c10 = result.get("kobak_common10_density", 0)
    c10_flag = " ⚠ Kobak common-10 cluster" if c10 > 20 else ""
    lines.append(f"Kobak common-10:     {c10:.1f}/1000 words{c10_flag}")

    em = result.get("em_dash_count", 0)
    em_note = " (house style: remove)" if em else ""
    lines.append(f"Em dashes:           {em}{em_note}")

    templates = result.get("syntactic_templates")
    if templates is not None:
        tr = templates["template_rate"]
        lines.append(
            f"Template rate:       {tr:.3f} "
            f"({templates['pos_token_count']} POS tokens; rises with length, "
            f"compare like-sized texts only)"
        )
    elif result.get("syntactic_templates_unavailable_reason"):
        lines.append("Template rate:       n/a (spaCy unavailable)")

    markers = result.get("signature_markers") or {}
    if markers:
        rendered = ", ".join(f"{k}×{v}" for k, v in sorted(markers.items()))
        lines.append(f"Signature markers:   {rendered}")

    lines.append("")

    # Sentence stats
    lines.append(
        f"Sentence lengths: mean={result.get('sentence_length_mean', 0):.1f}, "
        f"stdev={result.get('sentence_length_stdev', 0):.1f}, "
        f"min={result.get('sentence_length_min', 0)}, "
        f"max={result.get('sentence_length_max', 0)}"
    )
    lines.append("")

    # Findings
    findings = result["findings"]
    if findings:
        lines.append(f"── Findings ({len(findings)} sentences flagged) ──\n")
        for f in findings:
            lines.append(f"  [{f['line']}] {f['sentence']}")
            for issue in f["issues"]:
                lines.append(f"      → {issue}")
            lines.append("")
    else:
        lines.append("No per-sentence findings. Text looks clean.\n")

    # Dependencies status
    deps = []
    if not HAS_TEXTSTAT:
        deps.append("textstat (readability)")
    if not HAS_SPACY:
        deps.append("spacy+en_core_web_sm (passive voice)")
    if not HAS_LEXRICH:
        deps.append("lexicalrichness (MTLD/MATTR)")
    if deps:
        lines.append(f"Note: missing optional deps: {', '.join(deps)}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze text for AI-generated writing patterns."
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--file", type=str, help="Read from file instead of stdin")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file) as fh:
                text = fh.read()
        except FileNotFoundError:
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    else:
        text = sys.stdin.read()

    result = analyze_text(text)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(_format_human(result))


if __name__ == "__main__":
    main()
