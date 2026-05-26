"""Tests for analyze.py — AI slop detection tool."""

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

TOOL = str(Path(__file__).parent / "analyze.py")

# ---------------------------------------------------------------------------
# Fixtures — designed far from thresholds for stability
# ---------------------------------------------------------------------------

# Uniform sentence lengths, AI vocabulary, passive voice — classic AI slop
AI_TEXT = textwrap.dedent("""\
    The landscape of modern technology has undergone a transformative shift in recent years.
    This pivotal development delves into the multifaceted nature of digital innovation today.
    It is worth noting that the implications are significant for all stakeholders involved.
    The ecosystem has been fundamentally reshaped by these groundbreaking advancements overall.
    Each organization navigates this nuanced terrain with comprehensive and holistic approaches.
    The paradigm showcases how cutting-edge solutions foster synergy across the realm today.
    Moreover, this tapestry of innovation underscores the pivotal role of transformative tech.
    The landscape has been bolstered by meticulous efforts to streamline intricate processes.
    Furthermore, the comprehensive ecosystem elucidates the multifaceted interplay of factors.
    It is important to note that these developments have garnered significant attention lately.
""")

# Varied sentence lengths, no AI words, active voice, contractions
HUMAN_TEXT = textwrap.dedent("""\
    I fixed the bug Tuesday. Three hours of printf debugging — brutal.
    The parser choked on nested brackets because I'd forgotten to pop the stack after matching.
    Sarah caught it in review.
    We shipped the patch at 3am.
    Nobody complained, which honestly surprised me given how many users hit that endpoint daily.
    Next sprint I'm adding fuzz tests so we catch this stuff before it gets to prod.
""")

# Dedicated fixture: sentences with identical word counts for low burstiness
UNIFORM_SENTENCES = (
    "The system processes the input data. "
    "The module handles the output stream. "
    "The server manages the client request. "
    "The function returns the final result. "
    "The program validates the user input. "
    "The service monitors the active state. "
) * 3

# Dedicated fixture: wildly varied sentence lengths for high burstiness
VARIED_SENTENCES = (
    "No. "
    "I spent three weeks debugging that race condition in the connection pool and finally traced it "
    "to a missing mutex on the shared counter that two goroutines both wrote to under load. "
    "Fixed it. "
    "The whole cluster came back up, and latency dropped from 800ms p99 to under 12ms, which "
    "meant the on-call team could finally sleep through the night without getting paged every "
    "forty minutes about timeout errors that weren't even real timeouts. "
    "Done. "
)

# Dedicated fixture: heavy repetition for low TTR
REPETITIVE_TEXT = (
    "The system is good. The system is great. The system is fine. "
    "The system works well. The system runs well. The system performs well. "
    "The system is good. The system is great. The system is fine. "
    "The system handles things. The system manages things. The system does things. "
) * 3

# Dedicated fixture: passive voice
PASSIVE_TEXT = (
    "The report was written by the team. "
    "The system was tested by engineers. "
    "The decision was made by management. "
    "The code was reviewed by senior developers. "
    "The deployment was handled by operations. "
    "The bug was discovered during testing. "
)

SINGLE_SENTENCE = "Hello world."
EMPTY_TEXT = ""
WHITESPACE_TEXT = "   \n\n  \t  "


# ---------------------------------------------------------------------------
# Function-level tests (import analyze module directly)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def analyze_module():
    """Import analyze.py as a module."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("analyze", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestBurstiness:
    """Burstiness = stdev(sentence_lengths) / mean(sentence_lengths)."""

    def test_uniform_sentences_low_burstiness(self, analyze_module):
        result = analyze_module.analyze_text(UNIFORM_SENTENCES)
        assert result["burstiness"] < 0.2, f"Expected <0.2, got {result['burstiness']}"

    def test_varied_sentences_high_burstiness(self, analyze_module):
        result = analyze_module.analyze_text(VARIED_SENTENCES)
        assert result["burstiness"] > 0.5, f"Expected >0.5, got {result['burstiness']}"


class TestVocabularyDensity:
    """AI vocabulary density = count of Kobak words per 1000 words."""

    def test_ai_text_high_density(self, analyze_module):
        result = analyze_module.analyze_text(AI_TEXT)
        assert result["ai_vocabulary_density"] > 10, f"Expected >10, got {result['ai_vocabulary_density']}"

    def test_human_text_low_density(self, analyze_module):
        result = analyze_module.analyze_text(HUMAN_TEXT)
        assert result["ai_vocabulary_density"] < 5, f"Expected <5, got {result['ai_vocabulary_density']}"


class TestLexicalDiversity:
    """TTR = unique words / total words."""

    def test_repetitive_text_low_ttr(self, analyze_module):
        result = analyze_module.analyze_text(REPETITIVE_TEXT)
        assert result["ttr"] < 0.3, f"Expected <0.3, got {result['ttr']}"

    def test_human_text_higher_ttr(self, analyze_module):
        result = analyze_module.analyze_text(HUMAN_TEXT)
        assert result["ttr"] > 0.4, f"Expected >0.4, got {result['ttr']}"


class TestPassiveVoice:
    """Passive voice rate = passive sentences / total sentences."""

    def test_passive_text_high_rate(self, analyze_module):
        result = analyze_module.analyze_text(PASSIVE_TEXT)
        assert result["passive_voice_rate"] > 0.4, f"Expected >0.4, got {result['passive_voice_rate']}"

    def test_human_text_low_passive(self, analyze_module):
        result = analyze_module.analyze_text(HUMAN_TEXT)
        assert result["passive_voice_rate"] < 0.2, f"Expected <0.2, got {result['passive_voice_rate']}"


class TestReadability:
    """Flesch-Kincaid grade level via textstat."""

    def test_readability_present(self, analyze_module):
        result = analyze_module.analyze_text(AI_TEXT)
        assert "flesch_kincaid_grade" in result
        assert isinstance(result["flesch_kincaid_grade"], (int, float))


class TestFindings:
    """Per-sentence findings with locations."""

    def test_ai_text_has_findings(self, analyze_module):
        result = analyze_module.analyze_text(AI_TEXT)
        assert len(result["findings"]) > 0
        finding = result["findings"][0]
        assert "sentence" in finding
        assert "issues" in finding
        assert "line" in finding

    def test_human_text_fewer_findings(self, analyze_module):
        ai_result = analyze_module.analyze_text(AI_TEXT)
        human_result = analyze_module.analyze_text(HUMAN_TEXT)
        assert len(human_result["findings"]) < len(ai_result["findings"])


class TestEdgeCases:
    """Empty, whitespace, single sentence — no crashes."""

    def test_empty_text(self, analyze_module):
        result = analyze_module.analyze_text(EMPTY_TEXT)
        assert result["burstiness"] == 0
        assert result["ttr"] == 0
        assert len(result["findings"]) == 0

    def test_whitespace_only(self, analyze_module):
        result = analyze_module.analyze_text(WHITESPACE_TEXT)
        assert result["burstiness"] == 0

    def test_single_sentence(self, analyze_module):
        result = analyze_module.analyze_text(SINGLE_SENTENCE)
        assert result["burstiness"] == 0  # can't compute variance with 1 sentence


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------

class TestCLI:
    """Test the CLI interface (stdin, file, JSON output)."""

    def test_stdin_json_output(self):
        proc = subprocess.run(
            [sys.executable, TOOL, "--json"],
            input=AI_TEXT, capture_output=True, text=True, timeout=30
        )
        assert proc.returncode == 0, f"stderr: {proc.stderr}"
        data = json.loads(proc.stdout)
        expected_keys = {"burstiness", "ttr", "ai_vocabulary_density",
                         "passive_voice_rate", "flesch_kincaid_grade",
                         "sentence_count", "word_count", "findings"}
        assert expected_keys.issubset(data.keys()), f"Missing keys: {expected_keys - data.keys()}"

    def test_file_input(self, tmp_path):
        f = tmp_path / "sample.txt"
        f.write_text(HUMAN_TEXT)
        proc = subprocess.run(
            [sys.executable, TOOL, "--file", str(f), "--json"],
            capture_output=True, text=True, timeout=30
        )
        assert proc.returncode == 0, f"stderr: {proc.stderr}"
        data = json.loads(proc.stdout)
        assert data["word_count"] > 0

    def test_human_readable_output(self):
        proc = subprocess.run(
            [sys.executable, TOOL],
            input=HUMAN_TEXT, capture_output=True, text=True, timeout=30
        )
        assert proc.returncode == 0, f"stderr: {proc.stderr}"
        assert "Burstiness" in proc.stdout or "burstiness" in proc.stdout

    def test_invalid_file(self):
        proc = subprocess.run(
            [sys.executable, TOOL, "--file", "/nonexistent/file.txt", "--json"],
            capture_output=True, text=True, timeout=30
        )
        assert proc.returncode != 0

    def test_empty_stdin(self):
        proc = subprocess.run(
            [sys.executable, TOOL, "--json"],
            input="", capture_output=True, text=True, timeout=30
        )
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert data["word_count"] == 0
