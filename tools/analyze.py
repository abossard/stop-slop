#!/usr/bin/env python3
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

AI_VERBS = {
    "delve", "underscore", "showcase", "elucidate", "navigate",
    "foster", "leverage", "harness", "illuminate", "spearhead",
    "bolster", "streamline", "encompass", "revolutionize", "embark",
}

AI_ADJECTIVES = {
    "multifaceted", "pivotal", "nuanced", "holistic", "transformative",
    "comprehensive", "groundbreaking", "cutting-edge", "invaluable",
    "meticulous", "intricate", "commendable", "notable", "paramount",
}

AI_NOUNS = {
    "tapestry", "landscape", "paradigm", "synergy", "ecosystem",
    "realm", "cornerstone", "testament", "beacon", "catalyst",
    "underpinning", "interplay",
}

AI_TRANSITIONS = {
    "furthermore", "moreover", "notably", "consequently",
}

AI_PHRASES = [
    "it is worth noting", "it is important to note", "in the context of",
    "plays a crucial role", "sheds light on", "paves the way",
    "remains a significant challenge", "has garnered significant attention",
    "offers a promising avenue", "it is imperative to",
    "a comprehensive understanding", "in light of the above",
    "warrants further investigation", "a growing body of",
]

ALL_AI_WORDS = AI_VERBS | AI_ADJECTIVES | AI_NOUNS | AI_TRANSITIONS


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


def _compute_ai_vocab_density(words: list[str]) -> float:
    """Count AI vocabulary words per 1000 words."""
    if not words:
        return 0.0
    # Check individual words
    hits = sum(1 for w in words if w in ALL_AI_WORDS)
    # Check multi-word phrases in joined text
    joined = " ".join(words)
    for phrase in AI_PHRASES:
        hits += len(re.findall(re.escape(phrase), joined))
    return round(hits / len(words) * 1000, 2)


def _compute_passive_voice_rate(sentences: list[str]) -> float:
    """Fraction of sentences with passive voice (via spaCy or regex fallback)."""
    if not sentences:
        return 0.0

    passive_count = 0

    if HAS_SPACY:
        for sent in sentences:
            doc = _nlp(sent)
            has_passive = any(
                tok.dep_ in ("nsubjpass", "auxpass") for tok in doc
            )
            if has_passive:
                passive_count += 1
    else:
        # Regex fallback: "was/were/been/being + past participle pattern"
        passive_re = re.compile(
            r'\b(?:was|were|been|being|is|are|am)\s+\w+(?:ed|en|t)\b', re.IGNORECASE
        )
        for sent in sentences:
            if passive_re.search(sent):
                passive_count += 1

    return round(passive_count / len(sentences), 4)


def _compute_readability(text: str) -> float:
    """Flesch-Kincaid grade level."""
    if HAS_TEXTSTAT and text.strip():
        return round(textstat.flesch_kincaid_grade(text), 2)
    return 0.0


def _generate_findings(sentences: list[str], words: list[str]) -> list[dict]:
    """Per-sentence findings with line numbers and issues."""
    findings = []
    line = 1  # 1-indexed

    for sent in sentences:
        issues = []
        sent_words = _word_tokenize(sent)

        # Check AI vocabulary
        ai_words_found = [w for w in sent_words if w in ALL_AI_WORDS]
        if ai_words_found:
            issues.append(
                f"AI-overused words: {', '.join(ai_words_found)} "
                f"(Kobak et al. frequency ratios)"
            )

        # Check AI phrases
        sent_lower = sent.lower()
        for phrase in AI_PHRASES:
            if phrase in sent_lower:
                issues.append(f"AI-typical phrase: \"{phrase}\"")

        # Check passive voice (per-sentence)
        if HAS_SPACY:
            doc = _nlp(sent)
            if any(tok.dep_ in ("nsubjpass", "auxpass") for tok in doc):
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

        if issues:
            findings.append({
                "line": line,
                "sentence": sent[:120] + ("..." if len(sent) > 120 else ""),
                "issues": issues,
            })

        line += 1

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
            "findings": [],
        }

    sentences = _split_sentences(text)
    words = _word_tokenize(text)
    sentence_lengths = [len(_word_tokenize(s)) for s in sentences]

    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "burstiness": _compute_burstiness(sentence_lengths),
        "ttr": _compute_ttr(words),
        "ai_vocabulary_density": _compute_ai_vocab_density(words),
        "passive_voice_rate": _compute_passive_voice_rate(sentences),
        "flesch_kincaid_grade": _compute_readability(text),
        "sentence_length_mean": round(statistics.mean(sentence_lengths), 2) if sentence_lengths else 0,
        "sentence_length_stdev": round(statistics.stdev(sentence_lengths), 2) if len(sentence_lengths) >= 2 else 0,
        "sentence_length_min": min(sentence_lengths) if sentence_lengths else 0,
        "sentence_length_max": max(sentence_lengths) if sentence_lengths else 0,
        "findings": _generate_findings(sentences, words),
    }


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
            text = open(args.file).read()
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
