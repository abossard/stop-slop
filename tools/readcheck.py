#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "spacy>=3.8.0,<3.9",
#   "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl",
# ]
# ///
"""Find constructions that slow a reader down, as measured by Clark, Martin & Mahowald
(2026, arXiv:2610.29162): noun stacks, object relative clauses, human verbs on things
and long dependencies.

Usage:
  readcheck.py --file draft.md           # one line per finding
  readcheck.py --file draft.md --json    # counts, rates and findings
  echo "text" | readcheck.py

references/research.md lists where this differs from the paper's method.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

_missing_deps = []
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


# Inline code, URLs, paths and identifiers become this one word (paper, appendix A.5),
# so a sentence with code in it still parses as one sentence.
PLACEHOLDER = "Codetok"

NOUN_STACK_NOUNS = 3

# Sentence-length bins for standardizing dependency length (paper, appendix B.3).
# The paper weights the bins by Wikipedia; these weights are each bin's share of
# dependency arcs in the Brown corpus (1.05M words) parsed with en_core_web_sm.
LENGTH_BINS = [(1, 5), (6, 10), (11, 15), (16, 20), (21, 30)]
BIN_WEIGHTS = [0.0228, 0.1103, 0.1916, 0.2361, 0.4392]

# A finding threshold, not part of the paper: subject, verb and object this many
# words apart.
FAR_APART_WORDS = 10
CORE_RELATIONS = {"nsubj": "subject", "nsubjpass": "subject", "dobj": "object"}

# The paper judges each verb with a classifier. This list stands in for it: verbs
# from the paper's examples and others that need a person or an animal, minus the
# ones engineers use literally of software ("expects", "refuses", "knows", "sees").
HUMAN_VERBS = {
    "eat", "swallow", "bite", "chew", "digest", "choke",
    "promise", "forget", "remember", "hope", "wish", "want", "think", "believe",
    "understand", "misunderstand", "complain", "scream", "shout", "cry", "beg",
    "love", "hate", "fear", "worry", "care", "fight", "steal", "cheat",
}
THING_PRONOUNS = {"it", "this", "that", "these", "those"}
PERSON_NOUNS = {
    "user", "person", "people", "team", "developer", "engineer", "reader", "writer",
    "author", "maintainer", "reviewer", "customer", "admin", "administrator", "operator",
    "owner", "member", "student", "teacher", "colleague", "human", "man", "woman",
    "child", "kid", "everyone", "anyone", "someone", "nobody", "folk", "guy",
}

RELATIVIZER_TAGS = {"WDT", "WP"}
FINITE_TAGS = {"VBD", "VBP", "VBZ", "MD"}
# "the way it works" and "the day we met" drop "that" without an object gap.
ADVERBIAL_HEADS = {"way", "time", "reason", "moment", "day", "place", "year", "minute", "second", "point"}

ADVICE = {
    "noun stack": 'say how the nouns relate with "of", "for" or a clause',
    "no that": 'add "that" after the noun',
    "human verb on a thing": "say what the thing does or causes",
    "far apart": "move the two words next to each other",
}

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")
RULE_RE = re.compile(r"^\s*[-=*_ ]{3,}\s*$")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
TABLE_RULE_RE = re.compile(r"^\s*\|[\s:\-|]+\|\s*$")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+(.*)")
BLOCKQUOTE_RE = re.compile(r"^\s*>\s?")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
EMPHASIS_RE = re.compile(r"(\*\*|__|\*|_)(?=\S)(.+?)(?<=\S)\1")
# Inline code, a URL, or a bare path, snake_case, call(), camelCase, --flag or file name.
CODE_RE = re.compile(
    r"`+[^`\n]+`+|https?://\S+"
    r"|(?<![\w/])(?:[\w.-]*[/\\][\w./\\-]+|\w+_\w+|\w+\(\)|[a-z]+[A-Z]\w*|--[\w-]+"
    r"|\w+\.(?:md|py|ts|js|json|yml|yaml|sh|ps1|bicep|txt|cs))(?![\w/])"
)
SYMBOL_RE = re.compile("[\u2190-\u21ff\u2600-\u27bf\U0001f300-\U0001faff]|->|=>")


def _clean_inline(text: str) -> tuple[str, list[str]]:
    """The block as prose, and the code each placeholder stands for, in order."""
    code = []

    def placeholder(match) -> str:
        code.append(match.group(0))
        return f" {PLACEHOLDER} "

    text = LINK_RE.sub(r"\1", IMAGE_RE.sub(" ", text))
    text = CODE_RE.sub(placeholder, text)
    text = EMPHASIS_RE.sub(r"\2", EMPHASIS_RE.sub(r"\2", text))
    text = SYMBOL_RE.sub(" ; ", text)
    return " ".join(text.split()), code


def prose_blocks(text: str) -> list[tuple[str, list[str]]]:
    """Markdown to (prose, code) blocks. No block crosses a paragraph, list item or table cell.

    Code fences and headings are left out, as in the paper (appendix A.5).
    """
    blocks, paragraph, in_fence = [], [], False

    def flush():
        if paragraph:
            blocks.append(" ".join(paragraph))
            paragraph.clear()

    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            flush()
        elif in_fence:
            continue
        elif not line.strip() or HEADING_RE.match(line) or RULE_RE.match(line):
            flush()
        elif TABLE_ROW_RE.match(line):
            flush()
            if not TABLE_RULE_RE.match(line):
                blocks.extend(cell.strip() for cell in line.strip().strip("|").split("|") if cell.strip())
        elif item := LIST_ITEM_RE.match(line):
            flush()
            paragraph.append(item.group(1))
        else:
            paragraph.append(BLOCKQUOTE_RE.sub("", line.strip()))
    flush()
    return [(prose, code) for prose, code in map(_clean_inline, blocks) if prose]


def _words(sent) -> list:
    return [tok for tok in sent if not tok.is_punct and not tok.is_space]


def _shown(tok) -> str:
    """The token as the writer wrote it: a placeholder shows its code again."""
    return tok.doc.user_data.get("code", {}).get(tok.i, tok.text)


def _phrase(doc, first: int, last: int) -> str:
    return "".join(_shown(tok) + tok.whitespace_ for tok in doc[first:last + 1]).strip()


def noun_stacks(sent) -> list[str]:
    """Three or more common nouns that modify one head noun.

    Proper nouns stay in the phrase but are not counted, so a product name in
    front of a noun is not a stack. Two nouns joined by a hyphen count as one:
    the hyphen already shows the reader how they group.
    """
    stacks = []
    for tok in sent:
        if tok.pos_ not in ("NOUN", "PROPN") or tok.dep_ == "compound" or tok.text == PLACEHOLDER:
            continue
        chain, frontier = [tok], [tok]
        while frontier:
            for child in frontier.pop().children:
                if child.dep_ == "compound" and child.pos_ in ("NOUN", "PROPN") and child.text != PLACEHOLDER:
                    chain.append(child)
                    frontier.append(child)
        members = {member.i for member in chain}
        hyphen_joins = sum(
            1 for i in members if i + 2 in members and sent.doc[i + 1].text == "-"
        )
        if sum(member.pos_ == "NOUN" for member in chain) - hyphen_joins >= NOUN_STACK_NOUNS:
            stacks.append(_phrase(sent.doc, min(members), max(members)))
    return stacks


def object_relatives(sent) -> list[tuple[str, str, bool]]:
    """(kind, phrase, flag) for each object relative clause; kind is "with that" or "no that".

    A clause without "that" is flagged only when its subject is a noun: with a
    pronoun subject ("the file you sent") the short form is frequent and easy.
    """
    found = []
    for verb in sent:
        head = verb.head
        if verb.dep_ != "relcl" or verb.pos_ not in ("VERB", "AUX") or head.i > verb.i:
            continue
        clause = [tok for tok in verb.subtree if head.i < tok.i < verb.i]
        subject = next((c for c in verb.children if c.dep_ == "nsubj" and head.i < c.i < verb.i), None)
        relativizer = next(
            (tok for tok in clause if tok.tag_ in RELATIVIZER_TAGS or (tok.lower_ == "that" and tok.dep_ != "det")),
            None,
        )
        if subject is None or any(tok.tag_ in ("WP$", "WRB") for tok in clause):
            continue
        phrase = _phrase(sent.doc, head.i, verb.i)
        if relativizer is not None:
            if relativizer.i != subject.i and relativizer.dep_ not in ("nsubj", "nsubjpass"):
                found.append(("with that", phrase, False))
            continue
        finite = verb.tag_ in FINITE_TAGS or any(c.dep_ == "aux" for c in verb.children)
        if not finite or subject.left_edge.i != head.i + 1 or head.lemma_.lower() in ADVERBIAL_HEADS:
            continue
        found.append(("no that", phrase, subject.pos_ != "PRON"))
    return found


def _is_thing(subject) -> bool:
    if subject.text == PLACEHOLDER or subject.lower_ in THING_PRONOUNS:
        return True
    return subject.pos_ == "NOUN" and subject.lemma_.lower() not in PERSON_NOUNS


def human_verbs_on_things(sent) -> list[str]:
    return [
f"{_shown(tok)} ... {tok.head.text}" if tok.head.i - tok.i > 1 else f"{_shown(tok)} {tok.head.text}"
        for tok in sent
        if tok.dep_ == "nsubj" and tok.head.pos_ == "VERB" and tok.i < tok.head.i
        and tok.head.lemma_.lower() in HUMAN_VERBS and _is_thing(tok)
    ]


def dependency_arcs(sent) -> list[tuple[int, str, str, str]]:
    """(length in words, relation, dependent, head); punctuation and the root are left out."""
    words = _words(sent)
    position = {tok.i: index for index, tok in enumerate(words)}
    return [
        (abs(position[tok.i] - position[tok.head.i]), tok.dep_, _shown(tok), _shown(tok.head))
        for tok in words
        if tok.head.i != tok.i and tok.head.i in position
    ]


def length_bin(word_count: int) -> int | None:
    for index, (low, high) in enumerate(LENGTH_BINS):
        if low <= word_count <= high:
            return index
    return None


def standardized_dependency_length(bins: list[list[int]]) -> float | None:
    """Mean arc length as if the text had the reference mix of sentence lengths.

    bins holds [arc count, summed arc length] per length bin. Empty bins are
    skipped and the remaining weights rescaled.
    """
    total = weight = 0.0
    for (arcs, length), bin_weight in zip(bins, BIN_WEIGHTS):
        if arcs:
            total += bin_weight * length / arcs
            weight += bin_weight
    return round(total / weight, 3) if weight else None


def analyze_text(text: str) -> dict:
    counts = {"noun_stacks": 0, "object_relatives_no_that": 0, "object_relatives_with_that": 0,
              "human_verbs_on_things": 0, "far_apart": 0}
    bins = [[0, 0] for _ in LENGTH_BINS]
    words = sentences = over_30 = 0
    findings = []

    def add(kind: str, phrase: str, sent) -> None:
        sentence = _phrase(sent.doc, sent.start, sent.end - 1)
        findings.append({"kind": kind, "phrase": phrase, "advice": ADVICE[kind], "sentence": sentence})

    for doc, code in _nlp.pipe(prose_blocks(text), as_tuples=True):
        placeholders = [tok.i for tok in doc if tok.text == PLACEHOLDER]
        doc.user_data["code"] = dict(zip(placeholders, code))
        for sent in doc.sents:
            sent_words = [tok for tok in _words(sent) if tok.text != PLACEHOLDER and any(c.isalnum() for c in tok.text)]
            if not sent_words:
                continue
            words += len(sent_words)
            sentences += 1

            for phrase in noun_stacks(sent):
                counts["noun_stacks"] += 1
                add("noun stack", phrase, sent)
            for kind, phrase, flag in object_relatives(sent):
                counts["object_relatives_" + kind.replace(" ", "_")] += 1
                if flag:
                    add(kind, phrase, sent)
            for phrase in human_verbs_on_things(sent):
                counts["human_verbs_on_things"] += 1
                add("human verb on a thing", phrase, sent)

            arcs = dependency_arcs(sent)
            index = length_bin(len(_words(sent)))
            if index is None:
                over_30 += 1
            else:
                bins[index][0] += len(arcs)
                bins[index][1] += sum(arc[0] for arc in arcs)
            far = [arc for arc in arcs if arc[1] in CORE_RELATIONS and arc[0] >= FAR_APART_WORDS]
            for length, relation, dependent, head in far[:1]:
                counts["far_apart"] += 1
                first, second = (dependent, head) if relation != "dobj" else (head, dependent)
                add("far apart", f"{first} ... {second} ({length} words)", sent)

    return {
        "words": words,
        "sentences": sentences,
        "sentences_over_30_words": over_30,
        "counts": counts,
        "per_1000_words": {key: round(1000 * value / words, 2) if words else 0 for key, value in counts.items()},
        "dependency_length": standardized_dependency_length(bins),
        "dependency_bins": bins,
        "findings": findings,
    }


def format_findings(result: dict) -> str:
    if not result["findings"]:
        return "No findings."
    return "\n".join(
        f'{f["kind"]}: "{f["phrase"]}": {f["advice"]}. Sentence: "{f["sentence"][:120]}"'
        for f in result["findings"]
    )


def _missing_deps_banner() -> str:
    lines = ["READCHECK: REQUIRED DEPENDENCIES MISSING, NO RESULTS"]
    lines += [f"  {name}: {type(exc).__name__}: {exc}" for name, exc in _missing_deps]
    lines += [
        "  Fix with uv (zero setup): brew install uv, then run tools/readcheck",
        "  Fix with pip: pip install -r tools/requirements.txt && python -m spacy download en_core_web_sm",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Find constructions that slow a reader down.")
    parser.add_argument("--json", action="store_true", help="Print counts, rates and findings as JSON")
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
    print(json.dumps(result, indent=2) if args.json else format_findings(result))


if __name__ == "__main__":
    main()
