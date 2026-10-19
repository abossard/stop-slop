#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "textstat>=0.7.0",
#   "spacy>=3.8.0,<3.9",
#   "lexicalrichness>=0.5.0",
#   "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl",
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

# --- Required dependencies: main() prints a banner and exits 3 without them ---

_missing_deps = []

try:
    import textstat
except Exception as exc:
    _missing_deps.append(("textstat", exc))

_nlp = None
try:
    import spacy
except Exception as exc:
    _missing_deps.append(("spacy", exc))
else:
    try:
        _nlp = spacy.load("en_core_web_sm")
    except Exception as exc:
        _missing_deps.append(("en_core_web_sm", exc))

try:
    from lexicalrichness import LexicalRichness
except Exception as exc:
    _missing_deps.append(("lexicalrichness", exc))


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

# Defensive negation tails: a finished clause followed by a denial of a weaker
# claim the reader never made ("asserts elapsed time, not merely that an error
# came back"). Distinct from NEGATIVE_PARALLELISM_RES, which needs a "but"/"it's"
# alternative to complete the frame; here the denial stands alone. Sentences
# already claimed by negative parallelism are skipped in _generate_findings, so
# a "not X, but Y" frame is reported once. Doing that in control flow rather
# than a regex lookahead keeps the match independent of embedded periods, which
# the sentence splitter leaves inside a sentence ("not merely a v3.5 warning").
DEFENSIVE_NEGATION_RES = [
    re.compile(
        r",\s*(?:and\s+)?not\s+(?:merely|just|only|simply)\b",
        re.IGNORECASE,
    ),
    # The optional article owns its trailing whitespace. Writing it as
    # `(?:a|an|the)?\s*` after `not\s+` lets two quantifiers match the same
    # spaces, which backtracks quadratically on a long whitespace run
    # (8.2s on 20k spaces, measured).
    re.compile(
        r",\s*not\s+(?:(?:an?|the)\s+)?"
        r"(?:decorative|optional|cosmetic|throwaway|nicety|smoke test)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r",\s*not\s+(?:(?:an?|the)\s+)?"
        r"(?:complete|full|whole|final|entire|only)\b",
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

# Importance-inflation frames built on "decisive"/"decisively", where an
# ordinary fact is upgraded into a turning point. Matched as collocations
# because the bare adjective is ordinary in military, sports and election
# prose ("a decisive victory"). See references/phrases.md for the frame list,
# the rewrites and the sources.
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
LONG_SENTENCE_WORDS = 25
SUBJECT_VERB_GAP = 10
NOMINALIZATION_SUFFIXES = (
    "tion", "sion", "ment", "ance", "ence", "ity", "ness",
)
# Suffix matches that are ordinary nouns, not hidden verbs.
NOMINALIZATION_EXCLUDE = {"sentence", "section", "reference", "evidence"}

# Every entry appears in at least one fetched list, marked per line:
# PL  = plainlanguage.gov "Simple Words and Phrases", archived 2016-12-23:
#       https://web.archive.org/web/20161223073724/http://www.plainlanguage.gov/howto/wordsuggestions/simplewords.cfm
# PEC = Plain English Campaign "The A to Z of alternative words" (2001), archived 2020-01-09:
#       https://web.archive.org/web/20200109034429/http://www.plainenglish.co.uk/files/alternative.pdf
# Words already in ALL_AI_WORDS stay out, so one word yields one issue.
PLAIN_SWAPS = {
    "utilize": "use",  # PL; PEC "utilise"
    "utilization": "use",  # PL; PEC "utilisation"
    "in order to": "to",  # PL
    "due to the fact that": "because",  # PL "due to, since"; PEC "due to the fact of": because
    "prior to": "before",  # PL, PEC
    "subsequent to": "after",  # PEC
    "provide": "give",  # PL, PEC
    "purchase": "buy",  # PL, PEC
    "obtain": "get",  # PEC
    "commence": "start",  # PL, PEC
    "terminate": "end",  # PL, PEC
    "assist": "help",  # PL; PEC "assistance"
    "attempt": "try",  # PL, PEC
    "approximately": "about",  # PEC
    "sufficient": "enough",  # PL, PEC
    "numerous": "many",  # PL, PEC
    "initial": "first",  # PL
    "additional": "more",  # PL, PEC
    "modify": "change",  # PL; PEC "modification"
    "demonstrate": "show",  # PL, PEC
    "indicate": "show",  # PL, PEC
    "regarding": "about",  # PL, PEC
    "concerning": "about",  # PL, PEC
    "therefore": "so",  # PL
    "nevertheless": "but",  # PEC
    "however": "but",  # PL
    "facilitate": "help",  # PL, PEC
    "implement": "do",  # PEC "carry out, do"; PL "carry out, start"
    "objective": "goal",  # PL, PEC
    "requirement": "need",  # PL; PEC "requirements"
    "immediately": "now",  # PEC "at once, now"; PL "at once"
    "currently": "now",  # PL, PEC
    "frequently": "often",  # PL, PEC
    "persons": "people",  # PEC
    "reside": "live",  # PL, PEC
    "retain": "keep",  # PL, PEC
    "perform": "do",  # PL, PEC
    "establish": "set up",  # PL, PEC
    "finalize": "finish",  # PL; PEC "finalise"
    "equivalent": "equal",  # PEC
}
PLAIN_SINGLE_WORDS = {word for word in PLAIN_SWAPS if " " not in word}
PLAIN_PHRASE_RES = {
    phrase: re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE)
    for phrase in PLAIN_SWAPS if " " in phrase
}
MERMAID_WARN_NODES = 10
MERMAID_SPLIT_NODES = 20
MERMAID_LABEL_WORDS = 7
MERMAID_SUBGRAPH_DEPTH = 2
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")
BOLD_RE = re.compile(r"(\*\*|__)(.+?)\1", re.DOTALL)
MERMAID_ID = r"[A-Za-z_]\w*(?:-\w+)*"
# Flowchart shapes, longest delimiters first: (((x))) ((x)) ([x]) [[x]] [(x)] {{x}} [/x/] >x] [x] (x) {x}
NODE_LABEL_RE = re.compile(
    rf"\b({MERMAID_ID})\s*(?:"
    r"\(\(\((.*?)\)\)\)|\(\((.*?)\)\)|\(\[(.*?)\]\)|\[\[(.*?)\]\]|\[\((.*?)\)\]|\{\{(.*?)\}\}"
    r"|\[[/\\](.*?)[/\\]\]|>(.*?)\]|\[(.*?)\]|\((.*?)\)|\{(.*?)\})"
)
MERMAID_DIRECTIVE_RE = re.compile(
    r"^(?:%%|flowchart\b|graph\b|classDef\b|class\b|style\b|click\b|linkStyle\b|direction\b)",
    re.IGNORECASE,
)
MERMAID_PIPE_LABEL_RE = re.compile(r"\|[^|]*\|")
MERMAID_EDGE_TEXT_RE = re.compile(r"(?<![-.=<])(?:--|==|-\.)(?![-.=>])\s+.+?\s+(?=[-.=<]{2,})")
MERMAID_EDGE_RE = re.compile(r"<?[-.=]{2,}[>xo]?|&")
MERMAID_ID_RE = re.compile(MERMAID_ID)
SEQUENCE_MARKER_RE = re.compile(
    r"(?:^|[.;:,]\s+)(?:first|second|third|then|next|after that|finally)\b",
    re.IGNORECASE,
)

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-+*]\s+|\d+[.)]\s+)")
BLOCKQUOTE_RE = re.compile(r"^\s*>\s?")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
SENTENCE_BREAK_RE = re.compile(r"(?<=[.!?])\s+")
ORDERED_MARKER_RE = re.compile(r"\s*(?:>\s*)*\d+[.)]")
WORD_CHAR_RE = re.compile(r"\w")
INLINE_CODE_RE = re.compile(r"(?<!`)(`+)(?!`)[^`\n]+?(?<!`)\1(?!`)")
LINK_TARGET_RE = re.compile(r"(?<=\])\([^)\s]*(?:\s+\"[^\"]*\")?\)")
BARE_URL_RE = re.compile(r"https?://[^\s<>]*[^\s<>.,;:!?)\]]")


def _mask_non_prose(text: str) -> str:
    """Blank inline code, link targets and bare URLs, keeping every offset."""
    for pattern in (INLINE_CODE_RE, LINK_TARGET_RE, BARE_URL_RE):
        text = pattern.sub(lambda match: " " * len(match.group(0)), text)
    return text


def _trimmed_span(text: str, start: int, end: int) -> tuple[int, int] | None:
    """Return the non-space span inside text[start:end]."""
    segment = text[start:end]
    left = len(segment) - len(segment.lstrip())
    right = len(segment.rstrip())
    if left >= right:
        return None
    return start + left, start + right


def _sentence_spans_in_block(text: str, masked: str, start: int, end: int) -> list[dict]:
    """Split one prose block at sentence ends found in the masked text.

    Spans are trimmed on the original text, so leading or trailing inline
    code and URLs stay inside; parts with no word character are dropped.
    """
    trimmed = _trimmed_span(text, start, end)
    if trimmed is None:
        return []

    block_start, block_end = trimmed
    content = masked[block_start:block_end]
    cuts = [
        match.start() for match in SENTENCE_BREAK_RE.finditer(content)
        if not ORDERED_MARKER_RE.fullmatch(content[:match.start()])
    ]
    spans = []
    for left, right in zip([0] + cuts, cuts + [len(content)]):
        part = _trimmed_span(text, block_start + left, block_start + right)
        if part and WORD_CHAR_RE.search(masked[part[0]:part[1]]):
            spans.append({"start": part[0], "end": part[1]})
    return spans


def _fence_segments(text: str) -> list[tuple[str | None, int, list[tuple[int, int, int, str]]]]:
    """Split text at code fences into (fence, opening_line, lines) runs.

    fence is None for prose and the fence's info word (for example "mermaid")
    inside a fence. Each line is (line_no, start, end, text); delimiter lines
    are dropped.
    """
    segments = []
    fence, opened, lines = None, 0, []
    pos = 0
    for line_no, raw in enumerate(text.splitlines(keepends=True), 1):
        line = raw.rstrip("\r\n")
        start, pos = pos, pos + len(raw)
        match = FENCE_RE.match(line)
        if not match:
            lines.append((line_no, start, start + len(line), line))
            continue
        segments.append((fence, opened, lines))
        fence = (line[match.end():].split() or [""])[0].lower() if fence is None else None
        opened, lines = line_no, []
    segments.append((fence, opened, lines))
    return segments


def _split_sentence_spans(text: str, masked: str) -> list[dict]:
    """Split markdown prose into sentence spans. Code fences and tables are skipped.

    Headings and blockquote lines stand alone; a list item keeps its
    continuation lines, like a paragraph. Boundaries come from the masked text.
    """
    spans = []

    def emit(block):
        if block:
            spans.extend(_sentence_spans_in_block(text, masked, *block))

    for fence, _, lines in _fence_segments(masked):
        if fence is not None:
            continue
        block = None
        for _, start, end, line in lines:
            if not line.strip() or TABLE_ROW_RE.match(line):
                emit(block)
                block = None
            elif HEADING_RE.match(line) or BLOCKQUOTE_RE.match(line):
                emit(block)
                emit((start, end))
                block = None
            elif block is None or LIST_ITEM_RE.match(line):
                emit(block)
                block = (start, end)
            else:
                block = (block[0], end)
        emit(block)
    return spans


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
    """Suffix-strip a word to a lexicon entry; backs up spaCy lemmas."""
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
    """Single spaCy pass over the full text. Returns reusable parser data."""
    doc = _nlp(text)
    lemmas = {}
    for tok in doc:
        lower = tok.text.lower()
        if lower not in lemmas:
            lemmas[lower] = tok.lemma_.lower()

    return {"doc": doc, "lemmas": lemmas}


def _tokens_by_sentence(doc, sentence_spans: list[dict]) -> list[list]:
    """Map spaCy tokens to our markdown sentences by character offset, in one pass."""
    mapped = [[] for _ in sentence_spans]
    index = 0
    for tok in doc:
        if tok.is_space:
            continue
        while index < len(sentence_spans) and tok.idx >= sentence_spans[index]["end"]:
            index += 1
        if index == len(sentence_spans):
            break
        if tok.idx >= sentence_spans[index]["start"]:
            mapped[index].append(tok)
    return mapped


def _plain_base(word: str, lemma: str) -> str | None:
    if lemma in PLAIN_SINGLE_WORDS:
        return lemma
    base = _lemmatize_fallback(word, PLAIN_SINGLE_WORDS)
    return base if base in PLAIN_SINGLE_WORDS else None


def _plain_swap_hits(sent: str, tokens: list) -> list[tuple[str, str]]:
    hits = []
    occupied = []
    for phrase, pattern in PLAIN_PHRASE_RES.items():
        for match in pattern.finditer(sent):
            hits.append((match.group(0), PLAIN_SWAPS[phrase]))
            occupied.append(match.span())

    token_items = [
        (tok.text, tok.lower_, tok.lemma_.lower(), tok.idx, tok.idx + len(tok.text))
        for tok in tokens
        if not tok.is_punct and not tok.is_space
    ]
    sent_start = min((tok.idx for tok in tokens), default=0)

    for surface, lower, lemma, start, end in token_items:
        local = (start - sent_start, end - sent_start)
        if any(local[0] >= span[0] and local[1] <= span[1] for span in occupied):
            continue
        base = _plain_base(lower, lemma)
        if base:
            hits.append((surface, PLAIN_SWAPS[base]))
    return hits


def _is_nominalization(token) -> bool:
    word = token.text.lower().strip("'")
    if token.pos_ != "NOUN" or token.lemma_.lower() in NOMINALIZATION_EXCLUDE:
        return False
    return any(
        word.endswith(suffix) or word.endswith(suffix + "s")
        for suffix in NOMINALIZATION_SUFFIXES
    )


def _compute_nominalization_density(sentence_tokens: list[list], word_count: int) -> float:
    if word_count == 0:
        return 0.0
    count = sum(1 for tokens in sentence_tokens for tok in tokens if _is_nominalization(tok))
    return round(count / word_count * 1000, 2)


def _mean_dependency_distance(sentence_tokens: list[list]) -> float:
    sentence_means = []
    for tokens in sentence_tokens:
        clean = [tok for tok in tokens if not tok.is_punct]
        positions = {tok.i: idx for idx, tok in enumerate(clean)}
        distances = [
            abs(positions[tok.i] - positions[tok.head.i])
            for tok in clean
            if tok.head.i in positions and tok.head.i != tok.i
        ]
        if distances:
            sentence_means.append(statistics.mean(distances))
    if not sentence_means:
        return 0.0
    return round(statistics.mean(sentence_means), 4)


def _subject_verb_gaps(tokens: list) -> list[tuple[str, str, int]]:
    clean = [tok for tok in tokens if not tok.is_punct]
    positions = {tok.i: idx for idx, tok in enumerate(clean)}
    gaps = []
    for tok in clean:
        if tok.dep_ not in ("nsubj", "nsubjpass"):
            continue
        head = tok.head
        if head.i not in positions or head.pos_ not in ("VERB", "AUX"):
            continue
        gap = abs(positions[head.i] - positions[tok.i]) - 1
        if gap >= SUBJECT_VERB_GAP:
            gaps.append((tok.text, head.text, gap))
    return gaps


def _trailing_ing_clause(tokens: list) -> str | None:
    """Return the start of a comma-led -ing clause that runs to the sentence end."""
    words = [t for t in tokens if not t.is_punct and not t.is_space]
    for idx, tok in enumerate(tokens):
        if tok.text != ",":
            continue
        following = [t for t in tokens[idx + 1:] if not t.is_punct and not t.is_space]
        if not following:
            continue
        head = following[0]
        if head.tag_ != "VBG" or head.dep_ != "advcl" or head.right_edge.i < words[-1].i:
            continue
        take = 3 if len(following) >= 3 and following[1].lower_ in {"a", "an", "the"} else 2
        return " ".join(t.text for t in following[:take])
    return None


def _compute_textstat_metrics(text: str, sentence_tokens: list[list]) -> dict:
    if not text.strip():
        return {"smog_index": 0, "dale_chall_score": 0, "difficult_word_rate": 0}

    word_tokens = [
        tok for tokens in sentence_tokens for tok in tokens
        if not tok.is_punct and not tok.is_space and tok.is_alpha and tok.pos_ != "PROPN"
    ]
    difficult = sum(1 for tok in word_tokens if textstat.is_difficult_word(tok.text))
    denominator = len(word_tokens)

    return {
        "smog_index": round(textstat.smog_index(text), 2),
        "dale_chall_score": round(textstat.dale_chall_readability_score(text), 2),
        "difficult_word_rate": round(difficult / denominator, 4) if denominator else 0,
    }


def _find_mermaid_visuals(segments: list) -> list[dict]:
    """Size, label and nesting checks for each mermaid fence, bare IDs included."""
    findings = []
    for fence, opened, lines in segments:
        if fence != "mermaid":
            continue
        nodes = set()
        depth = 0
        depth_reported = False
        for line_no, _, _, line in lines:
            stripped = line.strip()
            if stripped.lower().startswith("subgraph"):
                depth += 1
                if depth > MERMAID_SUBGRAPH_DEPTH and not depth_reported:
                    findings.append({
                        "line": line_no,
                        "kind": "mermaid",
                        "issue": "Mermaid subgraph nesting exceeds depth 2",
                    })
                    depth_reported = True
                continue
            if stripped == "end":
                depth = max(0, depth - 1)
                continue
            if not stripped or MERMAID_DIRECTIVE_RE.match(stripped):
                continue

            # ponytail: regex Mermaid parser. Misses one-line `graph TD; A-->B` diagrams,
            # `~~~` links, numeric IDs and v11 `@{ shape }` nodes; swap in a real parser
            # if one lands in Python.
            for match in NODE_LABEL_RE.finditer(line):
                label = next(g for g in match.groups()[1:] if g is not None).strip().strip("\"'")
                if EMOJI_RE.search(label):
                    findings.append({"line": line_no, "kind": "emoji", "issue": "Emoji as decoration"})
                for label_line in re.split(r"<br\s*/?>", label, flags=re.IGNORECASE):
                    if len(_word_tokenize(label_line)) > MERMAID_LABEL_WORDS:
                        findings.append({
                            "line": line_no,
                            "kind": "mermaid",
                            "issue": "Mermaid label has more than 7 words",
                        })
                        break
            bare = NODE_LABEL_RE.sub(lambda match: match.group(1), line)
            bare = MERMAID_EDGE_TEXT_RE.sub("", MERMAID_PIPE_LABEL_RE.sub(" ", bare))
            for part in MERMAID_EDGE_RE.split(bare):
                node = part.split(":::")[0].strip().rstrip(";")
                if MERMAID_ID_RE.fullmatch(node):
                    nodes.add(node)

        count = len(nodes)
        if count > MERMAID_SPLIT_NODES:
            findings.append({"line": opened, "kind": "mermaid", "issue": f"Split Mermaid diagram ({count} nodes)"})
        elif count > MERMAID_WARN_NODES:
            findings.append({"line": opened, "kind": "mermaid", "issue": f"Mermaid diagram has {count} nodes"})
    return findings


def _paragraphs_for_steps(prose_lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Plain paragraphs (no lists, headings, quotes or tables) with their first line number."""
    paragraphs = []
    current = []
    first = 0
    for line_no, line in prose_lines + [(0, "")]:
        if not line.strip() or any(
            pattern.match(line) for pattern in (TABLE_ROW_RE, HEADING_RE, LIST_ITEM_RE, BLOCKQUOTE_RE)
        ):
            if current:
                paragraphs.append((first, " ".join(current)))
            current = []
            continue
        if not current:
            first = line_no
        current.append(line.strip())
    return paragraphs


def _detect_visuals(text: str, prose_word_count: int) -> tuple[list[dict], float]:
    segments = _fence_segments(text)
    findings = _find_mermaid_visuals(segments)

    prose_lines = []
    for fence, _, lines in segments:
        if fence is None:
            prose_lines.extend((line_no, line) for line_no, _, _, line in lines)
        else:
            prose_lines.append((0, ""))

    for line_no, line in prose_lines:
        stripped = line.lstrip()
        list_match = LIST_ITEM_RE.match(stripped)
        first_token = stripped[list_match.end():].split()[:1] if list_match else []
        if (HEADING_RE.match(stripped) and EMOJI_RE.search(stripped)) or (
            first_token and EMOJI_RE.search(first_token[0])
        ):
            findings.append({"line": line_no, "kind": "emoji", "issue": "Emoji as decoration"})

    for line_no, paragraph in _paragraphs_for_steps(prose_lines):
        if len(SEQUENCE_MARKER_RE.findall(paragraph)) >= 3:
            findings.append({
                "line": line_no,
                "kind": "steps",
                "issue": "Steps in prose: use a numbered list",
            })

    prose = _mask_non_prose("\n".join(line for _, line in prose_lines))
    bold = [
        match for match in BOLD_RE.finditer(prose)
        # ponytail: lowercase __name__ spans read as Python dunders, not bold.
        if not (match.group(1) == "__" and re.fullmatch(r"[a-z][a-z0-9_]*", match.group(2)))
    ]
    bold_density = round(len(bold) / prose_word_count * 100, 2) if prose_word_count else 0
    return findings, bold_density


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


def _compute_syntactic_templates(pos_tags: list[str]) -> dict | None:
    """POS n-gram template repetition (Shaib et al. 2024, arXiv:2407.00211).

    A template is a POS n-gram that repeats at least twice. The rate is the
    fraction of n-gram positions covered by a repeated n-gram, averaged over
    n in 4..8.

    The rate is NOT length-invariant: it climbs with document size because
    longer texts give every n-gram more chances to recur. Measured on one
    human-written corpus it ran 0.13 at 150 words and 0.61 at 28k words, so
    the number is only comparable between texts of similar length and carries
    no AI-like threshold.

    Returns None below TEMPLATE_MIN_TOKENS POS tokens.
    """
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


def _compute_passive_voice_rate(sentences: list[str], passive_data: list[bool]) -> float:
    """Fraction of sentences with passive voice."""
    if not sentences:
        return 0.0
    return round(sum(passive_data) / len(sentences), 4)


def _compute_readability(text: str) -> float:
    """Flesch-Kincaid grade level."""
    if text.strip():
        return round(textstat.flesch_kincaid_grade(text), 2)
    return 0.0


def _generate_findings(
    sentences: list[str], shown: list[str], spacy_lemmas: dict,
    passive_data: list[bool], sentence_tokens: list[list],
) -> list[dict]:
    """Per-sentence findings with sentence indices and issues."""
    findings = []

    for idx, sent in enumerate(sentences):
        issues = []
        sent_words = _word_tokenize(sent)
        tokens = sentence_tokens[idx]

        if len(sent_words) > LONG_SENTENCE_WORDS:
            issues.append(f"Long sentence ({len(sent_words)} words)")

        for found, plain in _plain_swap_hits(sent, tokens):
            issues.append(f'Plain word: "{found}" -> "{plain}"')

        nominalizations = [tok.text.lower() for tok in tokens if _is_nominalization(tok)]
        verb_count = sum(1 for tok in tokens if tok.pos_ in ("VERB", "AUX"))
        if len(nominalizations) >= 2 and len(nominalizations) > verb_count:
            issues.append(f"Nominalizations: {', '.join(nominalizations)}")

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
        if passive_data[idx] and not any(tok.dep_ == "agent" for tok in tokens):
            issues.append("Passive voice with no actor: name who does it")

        clause = _trailing_ing_clause(tokens)
        if clause:
            issues.append(f'Trailing -ing clause: "{clause}"')

        for subject, verb, gap in _subject_verb_gaps(tokens)[:1]:
            issues.append(
                f'Subject far from verb: "{subject}" ... "{verb}" ({gap} words apart)'
            )

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
        claimed_by_parallelism = False
        for hit in _match_labels(sent, NEGATIVE_PARALLELISM_RES):
            issues.append(f"Negative parallelism: \"{hit}\" — state the positive claim")
            claimed_by_parallelism = True
            break

        # Defensive negation tails, skipped when the sentence is already
        # reported above so one negation frame yields one issue.
        if not claimed_by_parallelism:
            for hit in _match_labels(sent, DEFENSIVE_NEGATION_RES):
                issues.append(
                    f"Defensive negation: \"{hit}\": cut the tail, the claim already stands"
                )
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
                "sentence": shown[idx][:120] + ("..." if len(shown[idx]) > 120 else ""),
                "issues": issues,
            })

    return findings


def analyze_text(text: str) -> dict:
    """Analyze text and return a metrics dictionary."""
    raw_text = text
    text = raw_text.strip()
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
            "long_sentence_count": 0,
            "plain_swap_count": 0,
            "nominalization_density": 0,
            "mean_dependency_distance": 0,
            "smog_index": 0,
            "dale_chall_score": 0,
            "difficult_word_rate": 0,
            "visual_findings": [],
            "bold_density": 0,
            "findings": [],
        }

    # Inline code, link targets and URLs become spaces, so offsets still line up.
    masked = _mask_non_prose(text)
    sentence_spans = _split_sentence_spans(text, masked)
    sentences = [masked[span["start"]:span["end"]].strip() for span in sentence_spans]
    shown = [text[span["start"]:span["end"]] for span in sentence_spans]
    prose_text = "\n".join(sentences)
    words = _word_tokenize(prose_text)
    sentence_lengths = [len(_word_tokenize(s)) for s in sentences]

    spacy_data = _spacy_analyze(masked)
    spacy_lemmas = spacy_data["lemmas"]
    sentence_tokens = _tokens_by_sentence(spacy_data["doc"], sentence_spans)
    # A passive counts only when its head verb sits in the same sentence;
    # masked code can otherwise hand one sentence's subject to the next verb.
    passive_data = [
        any(t.dep_ in ("nsubjpass", "auxpass") and tokens[0].i <= t.head.i <= tokens[-1].i for t in tokens)
        for tokens in sentence_tokens
    ]
    pos_tags = [
        tok.pos_
        for tokens in sentence_tokens
        for tok in tokens
        if not tok.is_punct
    ]
    findings = _generate_findings(sentences, shown, spacy_lemmas, passive_data, sentence_tokens)
    textstat_metrics = _compute_textstat_metrics(prose_text, sentence_tokens)
    visual_findings, bold_density = _detect_visuals(raw_text, len(words))

    result = {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "burstiness": _compute_burstiness(sentence_lengths),
        "ttr": _compute_ttr(words),
        "ai_vocabulary_density": _compute_ai_vocab_density(words, spacy_lemmas),
        "passive_voice_rate": _compute_passive_voice_rate(sentences, passive_data),
        "flesch_kincaid_grade": _compute_readability(prose_text),
        "hapax_ratio": _compute_hapax_ratio(words),
        "yules_k": _compute_yules_k(words),
        "contraction_rate": _compute_contraction_rate(prose_text, sentences),
        "signature_markers": _detect_signature_markers(prose_text),
        "tier2_density": _compute_lexicon_density(words, AI_TIER2_WORDS, spacy_lemmas),
        "kobak_common10_density": _compute_lexicon_density(
            words, KOBAK_COMMON_10, spacy_lemmas
        ),
        "em_dash_count": prose_text.count(EM_DASH),
        "syntactic_templates": _compute_syntactic_templates(pos_tags),
        "syntactic_templates_unavailable_reason": None,
        "sentence_length_mean": round(statistics.mean(sentence_lengths), 2) if sentence_lengths else 0,
        "sentence_length_stdev": round(statistics.stdev(sentence_lengths), 2) if len(sentence_lengths) >= 2 else 0,
        "sentence_length_min": min(sentence_lengths) if sentence_lengths else 0,
        "sentence_length_max": max(sentence_lengths) if sentence_lengths else 0,
        "long_sentence_count": sum(1 for length in sentence_lengths if length > LONG_SENTENCE_WORDS),
        "plain_swap_count": sum(
            1 for finding in findings for issue in finding["issues"]
            if issue.startswith("Plain word:")
        ),
        "nominalization_density": _compute_nominalization_density(
            sentence_tokens, len(words)
        ),
        "mean_dependency_distance": _mean_dependency_distance(sentence_tokens),
        "visual_findings": visual_findings,
        "bold_density": bold_density,
        "findings": findings,
    }
    result.update(textstat_metrics)

    # MTLD via lexicalrichness (requires enough words for stable measurement)
    if len(words) >= 50:
        try:
            lr = LexicalRichness(prose_text)
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
    lines.append(f"SMOG:                {result.get('smog_index', 0):.1f}")
    lines.append(f"Dale-Chall:          {result.get('dale_chall_score', 0):.1f}")
    lines.append(f"Difficult words:     {result.get('difficult_word_rate', 0):.1%}")
    lines.append(
        "Readability formulas explain roughly a quarter to a third of reader difficulty."
    )

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

    visual_findings = result.get("visual_findings") or []
    if visual_findings:
        lines.append(f"── Visual findings ({len(visual_findings)} flagged) ──\n")
        for finding in visual_findings:
            lines.append(f"  [{finding['line']}] {finding['issue']}")
        lines.append("")

    return "\n".join(lines)


def _missing_deps_banner() -> str:
    rule = "═" * 72
    lines = [rule, "  STOP-SLOP ANALYZER: REQUIRED DEPENDENCIES MISSING, NO RESULTS", rule]
    lines += [f"  ✗ {name}: {type(exc).__name__}: {exc}" for name, exc in _missing_deps]
    lines += [
        "",
        "  The analyzer needs spaCy with en_core_web_sm, textstat and lexicalrichness.",
        "  Fix with uv (zero setup): brew install uv, then run tools/slopometer",
        "  Fix with pip: pip install -r tools/requirements.txt && python -m spacy download en_core_web_sm",
        rule,
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze text for AI-generated writing patterns."
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--file", type=str, help="Read from file instead of stdin")
    args = parser.parse_args()

    # Exit codes: 1 missing input file, 2 bad arguments (argparse), 3 missing dependencies.
    if args.file:
        try:
            with open(args.file) as fh:
                text = fh.read()
        except FileNotFoundError:
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    else:
        text = sys.stdin.read()

    # Read input first: a caller that writes stdin before reading stderr
    # deadlocks on macOS pipes if we exit with the banner unread.
    if _missing_deps:
        print(_missing_deps_banner(), file=sys.stderr)
        sys.exit(3)

    result = analyze_text(text)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(_format_human(result))


if __name__ == "__main__":
    main()
