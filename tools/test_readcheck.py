"""Tests for readcheck.py. The flagged sentences are model output quoted in arXiv:2610.29162."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

TOOL = str(Path(__file__).parent / "readcheck.py")


@pytest.fixture(scope="module")
def readcheck():
    spec = importlib.util.spec_from_file_location("readcheck", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _findings(result: dict) -> list[tuple[str, str]]:
    return [(finding["kind"], finding["phrase"]) for finding in result["findings"]]


class TestFindings:
    @pytest.mark.parametrize("text,kind,phrase", [
        ("You've basically installed a horror movie soundtrack generator in your skull.",
         "noun stack", "horror movie soundtrack generator"),
        ("Our school could offer incentives like a community service honor cord at graduation.",
         "noun stack", "community service honor cord"),
        ("Three fail on the old code; the others check behaviour the old code never reached.",
         "no that", "behaviour the old code never reached"),
        ("`is_file()` swallows that and returns False.",
         "human verb on a thing", "`is_file()` swallows"),
        ("The whole conversation is eating its own tail.",
         "human verb on a thing", "conversation ... eating"),
        ("Policy 1 has a class-time shutdown requirement for phones.",
         "noun stack", "class-time shutdown requirement"),
        ("The guitar sitting in the corner because you're still deciding teaches you zero chords.",
         "far apart", "guitar ... teaches (10 words)"),
    ], ids=["stack-chat", "stack-essay", "no-that", "human-verb-code", "human-verb-chat", "stack-hyphen", "far-apart"])
    def test_paper_examples_flagged(self, readcheck, text, kind, phrase):
        assert (kind, phrase) in _findings(readcheck.analyze_text(text))

    @pytest.mark.parametrize("text", [
        "The coffee shop opens at nine.",
        "Azure Monitor Baseline Alerts ships the rules.",
        "It is a generator of horror-movie soundtracks.",
        "The file you sent is fine.",
        "The house that the contractors built is old.",
        "The parser reads the file and returns a list.",
        "The team wants a smaller diff.",
        "## Horror movie soundtrack generator",
        "```\nthe horror movie soundtrack generator swallows errors\n```",
        "",
    ], ids=["two-nouns", "product-name", "hyphen-pair", "pronoun-subject", "with-that", "plain-verb", "person-subject",
            "heading", "code-fence", "empty"])
    def test_controls_not_flagged(self, readcheck, text):
        assert readcheck.analyze_text(text)["findings"] == []

    def test_finding_quotes_the_original_sentence(self, readcheck):
        finding = readcheck.analyze_text("`load()` swallows the error from **every** lookup.")["findings"][0]
        assert finding["sentence"] == "`load()` swallows the error from every lookup."
        assert finding["advice"]


class TestCounts:
    @pytest.mark.parametrize("text,key", [
        ("The file you sent is fine.", "object_relatives_no_that"),
        ("The house that the contractors built is old.", "object_relatives_with_that"),
        ("The error message text is short.", "noun_stacks"),
        ("The cache forgets the entry after a minute.", "human_verbs_on_things"),
    ])
    def test_one_construction_counted(self, readcheck, text, key):
        result = readcheck.analyze_text(text)
        assert result["counts"][key] == 1
        assert result["per_1000_words"][key] == round(1000 / result["words"], 2)

    @pytest.mark.parametrize("text,words", [
        ("Run `make test` before you push.", 4),
        ("| Step | Note |\n|---|---|\n| Build | Takes two minutes. |", 6),
    ], ids=["inline-code-not-a-word", "table-cells"])
    def test_word_count(self, readcheck, text, words):
        assert readcheck.analyze_text(text)["words"] == words


class TestDependencyLength:
    @pytest.mark.parametrize("bins,expected", [
        ([[0, 0]] * 5, None),
        ([[10, 20], [0, 0], [0, 0], [0, 0], [0, 0]], 2.0),
        ([[10, 10], [10, 20], [10, 20], [10, 20], [10, 20]], 1.977),
    ], ids=["no-arcs", "one-bin", "weighted"])
    def test_standardized(self, readcheck, bins, expected):
        assert readcheck.standardized_dependency_length(bins) == expected

    def test_sentence_over_30_words_is_left_out(self, readcheck):
        result = readcheck.analyze_text(" ".join(["The dog saw the cat and"] * 6) + " left.")
        assert result["sentences_over_30_words"] == 1
        assert result["dependency_length"] is None


class TestCli:
    @pytest.mark.parametrize("args,text,expected", [
        ([], "The parser reads the file.", "No findings."),
        ([], "`is_file()` swallows that and returns False.", 'human verb on a thing: "`is_file()` swallows"'),
        (["--json"], "The parser reads the file.", '"dependency_length"'),
    ], ids=["clean", "finding", "json"])
    def test_output(self, args, text, expected):
        proc = subprocess.run([sys.executable, TOOL, *args], input=text, capture_output=True, text=True, timeout=120)
        assert proc.returncode == 0, proc.stderr
        assert expected in proc.stdout
