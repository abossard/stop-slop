"""Tests for analyze.py — AI slop detection tool."""

import json
import subprocess
import sys
import textwrap
import time
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

# Non-repeating human prose, long enough for stable template rates (C8).
# VARIED_SENTENCES * 3 would repeat verbatim and score ~1.0 templated,
# which would make the comparison vacuous.
VARIED_LONG_TEXT = HUMAN_TEXT + " " + VARIED_SENTENCES

SINGLE_SENTENCE = "Hello world."
EMPTY_TEXT = ""
WHITESPACE_TEXT = "   \n\n  \t  "

# Every signature marker from the model-era tic family (C1)
SIGNATURE_TEXT = (
    "That constraint is load-bearing for the whole design. "
    "The load bearing wall analogy keeps coming up. "
    "My honest take is that the migration slipped a week. "
    "You caught the regression, and that is not nothing. "
    "Sit with that for a moment before you reply. "
    "The word critical there is doing a lot of work. "
    "The structural seams of the abstraction are undocumented. "
)

# One marker buried in ~780 filler words: density stays far under 10/1000 (C2)
RARE_MARKER_TEXT = (
    "The team met on Tuesday and moved the task to the next column. " * 60
    + "That retry check is load-bearing."
)

# "decisive" in its importance-inflation frames (C11)
DECISIVE_TEXT = (
    "The migration proved decisive for the quarter. "
    "Leadership must act decisively on the remaining backlog."
)

# Tier-2 words with no other signal present (C6)
TIER2_ONLY_TEXT = "The comprehensive review gave us crucial insights this week."

# Tier-2 words sharing a sentence with a tier-1 word (C6)
TIER2_WITH_SIGNAL_TEXT = "The comprehensive review delves into crucial insights."

# Five of the Kobak common-10 words (C7)
COMMON10_TEXT = (
    "Additionally the comprehensive study exhibited crucial insights within scope."
)

# Exactly two em dashes (C10)
EM_DASH_TEXT = "The build broke — twice — before lunch."

REAL_BEFORE_AFTER_PAIRS = [
    (
        "pair 1",
        "Trigger: the coherent task or session boundary has been reached with no active criteria and no blocking issue, or the user explicitly requested extract. It turns raw outcomes into durable knowledge under `raw/`, `wiki/`, and `schema.md`.",
        "Turn this task's raw outcomes into durable knowledge under `raw/`, `wiki/`, and `schema.md`. Terminal phase, runs at most once.",
    ),
    (
        "pair 2",
        "The current pull request gives every child model one healthy dummy entity to confirm the deployment succeeded. The diagram labels that entity as a deployment check because it does not measure domain health. Replace it with the platform and system flows the domain provides.",
        "Add monitoring signals to each child model before using its state to assess domain health.",
    ),
    (
        "pair 3",
        "For each ALZ domains you might create a specific health model that represents the system flows of that domain, with the resources that contribute to it. You can use a mix of manually build entities and modelling and combine it with discovery rules for places where you don't control the life cycle of the contributing resources.",
        "Combine manually modeled entities with discovery rules where resources change often. Split paths that fail independently, set the rollup behavior on each parent entity, then set an objective on the root.",
    ),
    (
        "pair 9",
        textwrap.dedent("""\
            - Tick `[x]` on the criterion when its test goes green. **Do this immediately. Do not batch check-offs for later.**
            - Paste raw shortened evidence (command output, test result, key lines) directly under the criterion line. Every `[x]` must have its proof inline — a checkmark without evidence is not a checkmark.
            - If you resolve an unknown during implementation, add it to the Decisions table with its VOI level and source.
            - If you discover a requirement not in the original EARS, note it but do NOT add it to the criteria. That's review's job.
            - Work only on the current correction's active criteria. Archived criteria remain out of scope unless the blueprint marks their baseline proof invalidated.
        """).strip(),
        textwrap.dedent("""\
            - Tick `[x]` the moment its test goes green. **Do not batch check-offs for later.**
            - Paste raw shortened evidence (command output, test result, key lines) directly under the criterion line. A checkmark without inline proof is not a checkmark.
            - Add any unknown you resolved to the Decisions table with its VOI level and source.
            - Note a requirement you discover outside the original EARS, and leave it out of the criteria. Inspect owns that call.
            - Work only on the current correction's active criteria. Archived criteria stay out of scope unless the blueprint marks their baseline proof invalidated.
        """).strip(),
    ),
    (
        "pair 13",
        "What it does not carry is dependency. Every alert rule is deployed independently of every other one, so nothing in the system knows that an ExpressRoute circuit, a firewall and a gateway are three parts of one connectivity service. Three alerts fire, and a human decides whether that adds up to an outage.",
        "AMBA-ALZ does not model dependencies between alert rules. An ExpressRoute circuit, a firewall, and a gateway can support one connectivity service, but their alerts remain independent. An operator must assess their combined effect.",
    ),
    (
        "pair 14",
        textwrap.dedent("""\
            - **Fewer alerts, not fewer measurements.** Alerting moves from every rule to the entities you decide matter, so notification volume tracks the number of real problems rather than the size of the estate.
            - **Criticality is expressed once, in the graph.** A dependency says which components a service actually needs, so importance comes from position in the graph instead of a severity set per rule.
            - **Recovery is visible, and measurable.** You see when something clears, and how long it was broken.
        """).strip(),
        textwrap.dedent("""\
            - **Consolidated alerts.** Multiple signals determine one entity state. An alert on that entity fires once when its state changes to degraded or unhealthy.
            - **Explicit dependencies.** Relationships describe which components a service depends on and how their health affects the parent entity.
            - **Health history.** Graph and timeline views show current and past entity states.
        """).strip(),
    ),
    (
        "pair 15",
        "`harvest` also reads the persisted task brief's Decisions table and \"Discovered during review\" section to learn what categories of criteria the EARS consistently misses — that meta-learning feeds the director's process memory and sharpens future EARS nudges.",
        "`harvest` also reads the persisted task brief's Decisions table and \"Discovered during review\" section to learn what categories of criteria the EARS consistently misses. That meta-learning feeds the director's process memory and sharpens future EARS nudges.",
    ),
]

# Same clause skeleton repeated: high POS n-gram template rate (C8)
TEMPLATED_TEXT = (
    "The system processes the input data quickly. "
    "The module handles the output stream quickly. "
    "The server manages the client request quickly. "
    "The function returns the final result quickly. "
    "The program validates the user input quickly. "
    "The service monitors the active state quickly. "
    "The worker collects the pending message quickly. "
    "The router forwards the inbound packet quickly. "
)

# Structurally repeated but NOT verbatim-duplicated. TEMPLATED_TEXT * 2 would
# score exactly 1.0 through duplication alone, proving nothing (C8).
TEMPLATED_LONG_TEXT = TEMPLATED_TEXT + (
    "The handler accepts the queued payload quickly. "
    "The parser rejects the malformed header quickly. "
    "The client retries the failed upload quickly. "
    "The daemon reloads the changed config quickly. "
    "The broker drops the expired session quickly. "
    "The agent reports the current status quickly. "
    "The filter removes the duplicate record quickly. "
    "The cache evicts the coldest entry quickly. "
)


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


class TestMarkdownSplitter:
    """Markdown block boundaries shape prose metrics."""

    @pytest.mark.parametrize(
        "text,expected_sentences,expected_words",
        [
            ("# Setup\nInstall the package.\nRun tests.", 3, 6),
            ("- Install dependencies\n- Run tests", 2, 4),
            ("> Quote here\nNormal line", 2, 4),
            ("| key | value |\n| a | b |\n\nThe prose stays.", 1, 3),
            ("Before text.\n```python\nprint('hello world')\n```\nAfter text.", 2, 4),
            ("This sentence wraps\nacross one newline before it ends.", 1, 9),
            ("1. Stop the worker.\n2. Restart it.\n3. Check logs.", 3, 7),
            ("- `--json`\n- `--file`\n- https://example.com/a/b\n\n## `analyze.py`\n\n"
             "The tool reads input from stdin today.", 1, 7),
        ],
    )
    def test_markdown_boundaries(self, analyze_module, text, expected_sentences, expected_words):
        result = analyze_module.analyze_text(text)
        assert result["sentence_count"] == expected_sentences
        assert result["word_count"] == expected_words

    @pytest.mark.parametrize("text", [
        "1. Stop the worker.",
        "> 1. Quoted step one.\n> 2. Quoted step two.",
        "- `--json`\n- https://example.com/a/b\n\nThe tool reads input from stdin today.",
    ], ids=["ordered-marker", "quoted-ordered-marker", "code-only-items"])
    def test_no_empty_sentences(self, analyze_module, text):
        """C5-4 - markers and code-only blocks never become sentences."""
        result = analyze_module.analyze_text(text)
        assert result["sentence_length_min"] > 0

    def test_hard_wrapped_bullet_is_one_sentence(self, analyze_module):
        """C4-9 - a continuation line stays in its list item."""
        text = "- " + " ".join(["alpha"] * 15) + "\n  " + " ".join(["beta"] * 15) + "."
        result = analyze_module.analyze_text(text)
        assert result["sentence_count"] == 1
        assert result["long_sentence_count"] == 1


class TestLongSentences:
    """C0-2 - sentences over 25 words are flagged."""

    def test_25_words_not_flagged(self, analyze_module):
        text = " ".join(["alpha"] * 25) + "."
        result = analyze_module.analyze_text(text)
        assert result["long_sentence_count"] == 0
        assert not any("Long sentence" in i for i in _issues_of(result))

    def test_26_words_flagged(self, analyze_module):
        text = " ".join(["alpha"] * 26) + "."
        result = analyze_module.analyze_text(text)
        assert result["long_sentence_count"] == 1
        assert any("Long sentence (26 words)" == i for i in _issues_of(result))


class TestPlainWordSwaps:
    """C0-3 - plain alternatives are reported once."""

    @pytest.mark.parametrize(
        "text,issue",
        [
            ('We utilize the cache.', 'Plain word: "utilize" -> "use"'),
            ('The job utilizes the cache.', 'Plain word: "utilizes" -> "use"'),
            ('The cache was Utilized today.', 'Plain word: "Utilized" -> "use"'),
            ('Run this in order to finish.', 'Plain word: "in order to" -> "to"'),
            ('It failed due to the fact that the disk filled.', 'Plain word: "due to the fact that" -> "because"'),
            ('Stop the worker prior to deploy.', 'Plain word: "prior to" -> "before"'),
        ],
    )
    def test_plain_swaps_flagged(self, analyze_module, text, issue):
        result = analyze_module.analyze_text(text)
        assert issue in _issues_of(result)

    def test_plain_words_not_flagged(self, analyze_module):
        result = analyze_module.analyze_text(
            "We use the cache to finish because the disk filled before lunch."
        )
        assert not any("Plain word:" in i for i in _issues_of(result))

    def test_swap_list_has_no_ai_vocabulary(self, analyze_module):
        """One word yields one issue: AI-list words stay out of the swap list."""
        assert set(analyze_module.PLAIN_SWAPS) & analyze_module.ALL_AI_WORDS == set()

    def test_every_swap_listed_in_phrases_reference(self, analyze_module):
        """C0-15 - references/phrases.md lists the whole swap list."""
        phrases = (Path(__file__).parent.parent / "references" / "phrases.md").read_text()
        assert "## Plain Words" in phrases
        section = phrases.split("## Plain Words", 1)[1].split("\n## ", 1)[0]
        missing = [w for w in analyze_module.PLAIN_SWAPS if f"| {w} |" not in section]
        assert missing == []


class TestNonProseMasking:
    """C4-3 - link targets, bare URLs and inline code are not prose."""

    URL = "https://example.com/" + "/".join(f"segment{i}" for i in range(26))

    @pytest.mark.parametrize("template", [
        "Read [the guide]({url}) before you start the migration next week, please.",
        "Read the guide {url} before you start the migration next week, please.",
    ], ids=["markdown-link", "bare-url"])
    def test_url_is_not_prose(self, analyze_module, template):
        result = analyze_module.analyze_text(template.format(url=self.URL))
        assert result["long_sentence_count"] == 0
        assert result["word_count"] == 11

    @pytest.mark.parametrize("text", [
        "`template_rate` is reported without a threshold.",
        "We utilize the pool, see https://example.com/pool/docs",
    ], ids=["leading-code", "trailing-url"])
    def test_findings_show_original_sentence(self, analyze_module, text):
        """C5-3 - masked code and URLs stay visible in findings."""
        result = analyze_module.analyze_text(text)
        assert [f["sentence"] for f in result["findings"]] == [text]

    @pytest.mark.parametrize("text,flagged,words", [
        ("Call `utilize()` on the pool.", False, 4),
        ("We utilize the pool.", True, 4),
    ])
    def test_inline_code_is_not_prose(self, analyze_module, text, flagged, words):
        result = analyze_module.analyze_text(text)
        assert any("Plain word:" in i for i in _issues_of(result)) is flagged
        assert result["word_count"] == words


class TestNominalizations:
    """C0-4 - stacked zombie nouns are flagged."""

    def test_nominalization_stack_flagged(self, analyze_module):
        result = analyze_module.analyze_text(
            "The implementation of the configuration requires the utilization of resources."
        )
        assert result["nominalization_density"] > 0
        assert any(
            i == "Nominalizations: implementation, configuration, utilization"
            for i in _issues_of(result)
        )

    @pytest.mark.parametrize("text", [
        "We configured the service and deployed it twice.",
        "The configuration file lives in /etc.",
        "The sentence in this section cites the reference and its evidence.",
        "The references in each section give evidence for every sentence.",
    ])
    def test_nominalization_controls(self, analyze_module, text):
        result = analyze_module.analyze_text(text)
        assert not any("Nominalizations:" in i for i in _issues_of(result))


class TestAgentlessPassive:
    """C0-5 - only passive clauses without actors are findings."""

    def test_agentless_passive_flagged(self, analyze_module):
        result = analyze_module.analyze_text("The bug was discovered during testing.")
        assert "Passive voice with no actor: name who does it" in _issues_of(result)

    def test_passive_with_agent_not_flagged(self, analyze_module):
        result = analyze_module.analyze_text("The report was written by the team.")
        assert result["passive_voice_rate"] == 1.0
        assert not any("Passive voice with no actor" in i for i in _issues_of(result))


class TestMaskedPassive:
    """C5-2 - a passive counts only when its head verb is in the same sentence."""

    README_156 = (
        "`template_rate` is reported without a threshold. It is **not length-invariant**:\n"
        "on one human-written corpus it measured 0.13 at 150 words and 0.61 at 28,000\n"
        "words, because longer texts give every POS n-gram more chances to recur. Compare\n"
        "it only between texts of similar length. `pos_token_count` is reported alongside\n"
        "it so you can tell whether two numbers are comparable."
    )

    def test_imperative_after_code_led_sentence_not_passive(self, analyze_module):
        result = analyze_module.analyze_text(self.README_156)
        compare = [f for f in result["findings"] if f["sentence"].startswith("Compare")]
        assert not any("Passive voice" in i for f in compare for i in f["issues"])
        passive = [f["sentence"] for f in result["findings"] if any("Passive voice" in i for i in f["issues"])]
        assert any(s.startswith("`template_rate`") for s in passive)


class TestTrailingIngClause:
    """C0-6 - trailing present-participle clauses are flagged."""

    @pytest.mark.parametrize(
        "text,clause",
        [
            ("We shipped the patch, ensuring consistency across all regions.", "ensuring consistency"),
            ("The config is validated, highlighting the importance of careful review.", "highlighting the importance"),
        ],
    )
    def test_trailing_ing_flagged(self, analyze_module, text, clause):
        result = analyze_module.analyze_text(text)
        assert any(f'Trailing -ing clause: "{clause}"' in i for i in _issues_of(result))

    @pytest.mark.parametrize("text", [
        "Running the tests takes ten minutes.",
        "We kept testing the parser.",
        "After the release, using the new flag, we restarted the service.",
    ])
    def test_trailing_ing_controls(self, analyze_module, text):
        result = analyze_module.analyze_text(text)
        assert not any("Trailing -ing clause" in i for i in _issues_of(result))


class TestSubjectVerbDistance:
    """C0-7 - long subject to verb gaps are flagged."""

    def test_far_subject_verb_flagged(self, analyze_module):
        result = analyze_module.analyze_text(
            "The service, which was deployed last week by the operations team after several delays, crashed."
        )
        assert result["mean_dependency_distance"] is not None
        assert any(
            'Subject far from verb: "service" ... "crashed"' in i
            for i in _issues_of(result)
        )

    def test_close_subject_verb_not_flagged(self, analyze_module):
        result = analyze_module.analyze_text(
            "The service crashed after the operations team deployed it last week."
        )
        assert not any("Subject far from verb" in i for i in _issues_of(result))


class TestReadabilityBattery:
    """C0-8 - textstat metrics are additive JSON keys."""

    def test_readability_keys_present(self, analyze_module):
        result = analyze_module.analyze_text(AI_TEXT)
        assert isinstance(result["smog_index"], (int, float))
        assert isinstance(result["dale_chall_score"], (int, float))
        assert isinstance(result["difficult_word_rate"], (int, float))

    def test_empty_input_has_new_keys(self, analyze_module):
        result = analyze_module.analyze_text("")
        for key in [
            "long_sentence_count",
            "plain_swap_count",
            "nominalization_density",
            "mean_dependency_distance",
            "smog_index",
            "dale_chall_score",
            "difficult_word_rate",
        ]:
            assert key in result

    def test_human_output_mentions_formula_limits(self, analyze_module):
        result = analyze_module.analyze_text(AI_TEXT)
        output = analyze_module._format_human(result)
        assert "quarter to a third" in output


class TestCompletenessDenial:
    """C0-9 - completeness denials are defensive negation."""

    def test_completeness_denial_flagged(self, analyze_module):
        result = analyze_module.analyze_text(
            "This policy is one hardening step, not the complete fix for it."
        )
        assert any("Defensive negation" in i for i in _issues_of(result))

    def test_plain_contrast_not_flagged(self, analyze_module):
        result = analyze_module.analyze_text("Use the API, not the CLI.")
        assert not any("Defensive negation" in i for i in _issues_of(result))


def _visual_issues(result: dict) -> list[str]:
    return [finding["issue"] for finding in result["visual_findings"]]


def _total_issue_count(result: dict) -> int:
    return sum(len(finding["issues"]) for finding in result["findings"]) + len(result["visual_findings"])


def _mermaid_nodes(count: int) -> str:
    lines = ["```mermaid", "flowchart TD"]
    lines.extend(f"  n{i}[Node {i}]" for i in range(1, count + 1))
    lines.append("```")
    return "\n".join(lines)


class TestMermaidVisuals:
    """C1-2 - Mermaid diagram size and label checks."""

    @pytest.mark.parametrize(
        "node_count,expected",
        [
            (10, None),
            (11, "Mermaid diagram has 11 nodes"),
            (21, "Split Mermaid diagram"),
        ],
    )
    def test_mermaid_node_count(self, analyze_module, node_count, expected):
        result = analyze_module.analyze_text(_mermaid_nodes(node_count))
        issues = _visual_issues(result)
        if expected is None:
            assert not any("Mermaid diagram" in issue for issue in issues)
        else:
            assert any(expected in issue for issue in issues)

    @pytest.mark.parametrize(
        "label,flagged",
        [
            ("one two three four five six seven", False),
            ("one two three four five six seven eight", True),
        ],
    )
    def test_mermaid_label_words(self, analyze_module, label, flagged):
        text = f"```mermaid\nflowchart TD\n  A[{label}]\n```"
        result = analyze_module.analyze_text(text)
        has_label_issue = any("Mermaid label" in issue for issue in _visual_issues(result))
        assert has_label_issue is flagged

    @pytest.mark.parametrize(
        "body,flagged",
        [
            ("subgraph A\nsubgraph B\nx[Node]\nend\nend", False),
            ("subgraph A\nsubgraph B\nsubgraph C\nx[Node]\nend\nend\nend", True),
        ],
    )
    def test_mermaid_subgraph_depth(self, analyze_module, body, flagged):
        text = f"```mermaid\nflowchart TD\n{body}\n```"
        result = analyze_module.analyze_text(text)
        has_depth_issue = any("subgraph nesting" in issue for issue in _visual_issues(result))
        assert has_depth_issue is flagged

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("```mermaid\nflowchart LR\n  " + " --> ".join(f"N{i}" for i in range(1, 26)) + "\n```",
             "Split Mermaid diagram (25 nodes)"),
            ("```mermaid\nflowchart TD\n  A --> B & C & D\n  B --> E & F\n  C --> G & H\n"
             "  D --> I & J\n  E --> K & L\n  A --> L\n```", "Mermaid diagram has 12 nodes"),
            ("~~~mermaid\nflowchart TD\n" + "\n".join(f"  n{i}[Node {i}]" for i in range(1, 13)) + "\n~~~",
             "Mermaid diagram has 12 nodes"),
            ("```mermaid\nflowchart TD\n" + "\n".join(f"  A{i % 10} -- yes --> A{(i + 1) % 10}" for i in range(30))
             + "\n```", None),
            ("```mermaid\nflowchart TD\n" + "\n".join(f"  n{i}((Node {i}))" for i in range(1, 22)) + "\n```",
             "Split Mermaid diagram (21 nodes)"),
            ("```mermaid\nflowchart TD\n" + "\n".join("  h" + str(i) + "{{Hex " + str(i) + "}}" for i in range(1, 22))
             + "\n```", "Split Mermaid diagram (21 nodes)"),
            ("```mermaid\nflowchart LR\n  A((circle)) --> B{{hex}} --> C(((dbl))) --> D>asym] --> E[/para/]"
             " --> F[(db)] --> G([stad]) --> H[[sub]] --> I --> J --> K\n```", "Mermaid diagram has 11 nodes"),
            ("```mermaid\nflowchart TD\n  A -- go --- B\n  B -- re-run --> C\n  C -->|go| D\n  D -. maybe .-> E\n"
             "  E == yes ==> F\n  F --- G\n  G --> H\n  H --> I\n  I --> J\n```", None),
        ],
        ids=["bare-chain-25", "chained-edges-12", "tilde-fence-12", "repeated-ids-edge-text-10",
             "circles-21", "hexagons-21", "mixed-shapes-11", "edge-text-10"],
    )
    def test_mermaid_unique_node_ids(self, analyze_module, text, expected):
        """C4-2 - count unique IDs, bare or labelled, in either fence style."""
        issues = _visual_issues(analyze_module.analyze_text(text))
        if expected is None:
            assert not any("Mermaid diagram" in issue for issue in issues), issues
        else:
            assert expected in issues, issues

    def test_plan_summary_design_diagram_has_no_node_count_finding(self, analyze_module):
        diagram = textwrap.dedent("""\
            ```mermaid
            flowchart TD
              IN["input text"] --> SPLIT["_split_sentences<br/>markdown-aware, skips code fences"]
              IN --> NLP["_spacy_analyze<br/>one parse"]
              NLP --> MAP["tokens per sentence<br/>by char offset"]
              SPLIT --> MAP
              MAP --> DET["per-sentence detectors<br/>existing + long,<br/>plain word, nominalization"]
              NLP --> DOC["doc metrics<br/>mean dependency distance"]
              IN --> TS["textstat<br/>FKGL + SMOG + Dale-Chall"]
              DET --> OUT["JSON / human report"]
              DOC --> OUT
              TS --> OUT
              IN --> VIS["_detect_visuals<br/>mermaid, emoji, steps in prose, bold_density"]
              VIS --> OUT
            ```
        """)
        result = analyze_module.analyze_text(diagram)
        assert not any("Mermaid diagram" in issue for issue in _visual_issues(result))


class TestDecorativeEmoji:
    """C1-3 - emoji as decoration is visual slop."""

    @pytest.mark.parametrize("text", [
        "## 🚀 Setup",
        "- ✅ Done",
        "```mermaid\nflowchart TD\n  A[✅ Done]\n```",
    ])
    def test_decorative_emoji_flagged(self, analyze_module, text):
        result = analyze_module.analyze_text(text)
        assert any("Emoji as decoration" in issue for issue in _visual_issues(result))

    def test_running_text_emoji_not_flagged(self, analyze_module):
        result = analyze_module.analyze_text("Ship it 🎉 today.")
        assert not any("Emoji as decoration" in issue for issue in _visual_issues(result))


class TestBoldDensity:
    """C1-4 - bold spans are a metric only."""

    def test_bold_density(self, analyze_module):
        result = analyze_module.analyze_text("**Bold** plain words here. __Strong__ more prose now.")
        assert result["bold_density"] == 25.0
        assert result["visual_findings"] == []

    def test_empty_bold_density(self, analyze_module):
        assert analyze_module.analyze_text("")["bold_density"] == 0

    @pytest.mark.parametrize("text", [
        "Plain words here.\n```python\nx = a**b**c\n```",
        "Pass `**kwargs**` to the call.",
        "Override __init__ and __repr__ in the class.",
    ], ids=["fence", "inline-code", "dunder"])
    def test_bold_density_ignores_code(self, analyze_module, text):
        """C4-8 - only prose bold counts."""
        assert analyze_module.analyze_text(text)["bold_density"] == 0


class TestStepsInProse:
    """C1-5 - dense sequences belong in numbered lists."""

    def test_steps_in_prose_flagged(self, analyze_module):
        text = "First, stop the worker, then clear the queue. Next, restart it. Finally, check logs."
        result = analyze_module.analyze_text(text)
        assert any("Steps in prose: use a numbered list" in issue for issue in _visual_issues(result))

    def test_two_markers_not_flagged(self, analyze_module):
        result = analyze_module.analyze_text("First, stop the worker, then restart it.")
        assert not any("Steps in prose" in issue for issue in _visual_issues(result))

    def test_numbered_list_not_flagged(self, analyze_module):
        text = "1. First, stop the worker.\n2. Then restart it.\n3. Finally, check logs."
        result = analyze_module.analyze_text(text)
        assert not any("Steps in prose" in issue for issue in _visual_issues(result))


class TestVisualFindingsContract:
    """C1-7 - visual findings use source line numbers."""

    def test_empty_and_plain_prose_visual_findings(self, analyze_module):
        assert analyze_module.analyze_text("")["visual_findings"] == []
        assert analyze_module.analyze_text("Plain prose only.")["visual_findings"] == []

    def test_visual_findings_shape_and_line(self, analyze_module):
        result = analyze_module.analyze_text("\nIntro.\n## 🚀 Setup")
        assert result["visual_findings"] == [
            {"line": 3, "kind": "emoji", "issue": "Emoji as decoration"}
        ]

    def test_human_output_prints_visual_findings(self, analyze_module):
        result = analyze_module.analyze_text(_mermaid_nodes(11))
        output = analyze_module._format_human(result)
        assert "Visual findings" in output


class TestRealBeforeAfterRegression:
    """C0-11 - real owner edits should reduce issue counts."""

    def test_regression_set_has_at_least_six_pairs(self):
        assert len(REAL_BEFORE_AFTER_PAIRS) >= 6

    @pytest.mark.parametrize("pair_id,before,after", REAL_BEFORE_AFTER_PAIRS)
    def test_before_has_more_issues_than_after(self, analyze_module, pair_id, before, after):
        before_count = _total_issue_count(analyze_module.analyze_text(before))
        after_count = _total_issue_count(analyze_module.analyze_text(after))
        assert before_count > after_count, (
            f"{pair_id}: before={before_count}, after={after_count}"
        )


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


class TestInflection:
    """Inflected forms of AI words must be detected (F1 fix)."""

    def test_verb_inflections_detected(self, analyze_module):
        text = (
            "The researcher delves into the topic. "
            "The team showcases their results. "
            "They fostered a culture of innovation. "
            "She is leveraging new technology. "
            "He bolstered the argument effectively."
        )
        result = analyze_module.analyze_text(text)
        assert result["ai_vocabulary_density"] > 30, (
            f"Inflected verbs not detected. Density: {result['ai_vocabulary_density']}"
        )

    def test_noun_plurals_detected(self, analyze_module):
        text = "The paradigms and ecosystems create synergies across realms."
        result = analyze_module.analyze_text(text)
        assert result["ai_vocabulary_density"] > 50, (
            f"Plural nouns not detected. Density: {result['ai_vocabulary_density']}"
        )


class TestMTLD:
    """MTLD metric from lexicalrichness (F3 fix)."""

    def test_mtld_present_for_long_text(self, analyze_module):
        # AI_TEXT is ~100 words, should be enough for MTLD
        result = analyze_module.analyze_text(AI_TEXT)
        assert "mtld" in result

    def test_mtld_none_for_short_text(self, analyze_module):
        result = analyze_module.analyze_text(SINGLE_SENTENCE)
        assert result["mtld"] is None


class TestHapaxRatio:
    """Hapax legomena ratio = words appearing once / unique words.
    AI: 0.45-0.60, Human: 0.60-0.85 (Opara 2024, StyloAI)."""

    def test_repetitive_text_low_hapax(self, analyze_module):
        result = analyze_module.analyze_text(REPETITIVE_TEXT)
        assert result["hapax_ratio"] is not None
        assert result["hapax_ratio"] < 0.15, (
            f"Repetitive text should have very low hapax ratio, got {result['hapax_ratio']}"
        )

    def test_ai_text_has_hapax(self, analyze_module):
        result = analyze_module.analyze_text(AI_TEXT)
        assert result["hapax_ratio"] is not None

    def test_human_text_higher_hapax_than_repetitive(self, analyze_module):
        result_human = analyze_module.analyze_text(HUMAN_TEXT)
        result_rep = analyze_module.analyze_text(REPETITIVE_TEXT)
        if result_human["hapax_ratio"] is not None and result_rep["hapax_ratio"] is not None:
            assert result_human["hapax_ratio"] > result_rep["hapax_ratio"], (
                f"Human hapax={result_human['hapax_ratio']} should be > "
                f"repetitive hapax={result_rep['hapax_ratio']}"
            )

    def test_none_for_short_text(self, analyze_module):
        result = analyze_module.analyze_text(SINGLE_SENTENCE)
        assert result["hapax_ratio"] is None


class TestYulesK:
    """Yule's K = 10⁴ × (M₂ − N) / N². Higher = more repetitive.
    AI: 80-200, Human: 20-100 (multi_detector.py, Retengart)."""

    def test_repetitive_text_high_k(self, analyze_module):
        result = analyze_module.analyze_text(REPETITIVE_TEXT)
        assert result["yules_k"] is not None
        assert result["yules_k"] > 80, (
            f"Repetitive text should have high Yule's K, got {result['yules_k']}"
        )

    def test_varied_text_lower_k(self, analyze_module):
        result_rep = analyze_module.analyze_text(REPETITIVE_TEXT)
        long_varied = VARIED_SENTENCES * 3
        result_var = analyze_module.analyze_text(long_varied)
        if result_var["yules_k"] is not None and result_rep["yules_k"] is not None:
            assert result_var["yules_k"] < result_rep["yules_k"], (
                f"Varied text K={result_var['yules_k']} should be < "
                f"repetitive text K={result_rep['yules_k']}"
            )

    def test_none_for_short_text(self, analyze_module):
        result = analyze_module.analyze_text(SINGLE_SENTENCE)
        assert result["yules_k"] is None


class TestContractionRate:
    """Contraction rate = contractions per sentence. AI uses fewer."""

    def test_human_text_has_contractions(self, analyze_module):
        result = analyze_module.analyze_text(HUMAN_TEXT)
        assert result["contraction_rate"] > 0, (
            f"Human text with contractions should have rate > 0, got {result['contraction_rate']}"
        )

    def test_ai_text_no_contractions(self, analyze_module):
        result = analyze_module.analyze_text(AI_TEXT)
        assert result["contraction_rate"] == 0, (
            f"AI text fixture has no contractions, expected rate 0, got {result['contraction_rate']}"
        )


class TestSentenceStarters:
    """AI-typical sentence starters produce per-sentence findings."""

    def test_ai_starters_flagged(self, analyze_module):
        text = (
            "Furthermore, the system processes data efficiently. "
            "Moreover, the architecture supports scaling. "
            "Additionally, the team implemented caching. "
            "The server handles requests well."
        )
        result = analyze_module.analyze_text(text)
        starter_findings = [
            f for f in result["findings"]
            if any("AI-typical starter" in i for i in f["issues"])
        ]
        assert len(starter_findings) == 3, (
            f"Expected 3 AI-starter findings, got {len(starter_findings)}"
        )

    def test_normal_starters_not_flagged(self, analyze_module):
        result = analyze_module.analyze_text(HUMAN_TEXT)
        starter_findings = [
            f for f in result["findings"]
            if any("AI-typical starter" in i for i in f["issues"])
        ]
        assert len(starter_findings) == 0, (
            f"Human text should have no AI-starter findings, got {len(starter_findings)}"
        )


def _issues_of(result: dict) -> list[str]:
    """Flatten every issue string across all findings."""
    return [issue for f in result["findings"] for issue in f["issues"]]


class TestSignatureMarkers:
    """C1/C2 — model-era tics are counted by occurrence, not by density."""

    def test_signature_markers_all_detected(self, analyze_module):
        result = analyze_module.analyze_text(SIGNATURE_TEXT)
        markers = result["signature_markers"]
        expected = {
            "load-bearing", "honest take", "not nothing",
            "sit with that", "doing a lot of work", "seam",
        }
        assert expected <= set(markers), f"Missing: {expected - set(markers)}"
        assert all(markers[m] >= 1 for m in expected), markers
        assert markers["load-bearing"] == 2, "both spellings must count"

    def test_rare_marker_survives_density_floor(self, analyze_module):
        result = analyze_module.analyze_text(RARE_MARKER_TEXT)
        assert result["word_count"] > 600, result["word_count"]
        assert result["ai_vocabulary_density"] < 10, (
            "premise broken: density must stay under the flag threshold, "
            f"got {result['ai_vocabulary_density']}"
        )
        assert result["signature_markers"].get("load-bearing") == 1
        assert any("load-bearing" in i for i in _issues_of(result)), (
            "single rare marker must still produce a per-sentence finding"
        )

    @pytest.mark.parametrize("sentence", [
        "The coal seam runs beneath the valley for three kilometres.",
        "Seam carving is a content-aware image resizing algorithm.",
        "She reinforced the seam with a double stitch.",
        "Check the weld seam for porosity before shipping.",
    ])
    def test_literal_domain_nouns_not_flagged(self, analyze_module, sentence):
        """`seam` is an ordinary noun in geology, imaging, sewing and welding."""
        result = analyze_module.analyze_text(sentence)
        assert result["signature_markers"] == {}, (
            f"false positive on: {sentence!r} -> {result['signature_markers']}"
        )

    def test_metaphorical_seam_flagged(self, analyze_module):
        result = analyze_module.analyze_text(
            "The load-bearing seams of the design are undocumented."
        )
        assert result["signature_markers"].get("seam") == 1

    def test_clean_text_has_no_markers(self, analyze_module):
        result = analyze_module.analyze_text(HUMAN_TEXT)
        assert result["signature_markers"] == {}


class TestNegativeParallelism:
    """C3 — negation-then-correction frames, without flagging plain negation."""

    @pytest.mark.parametrize("sentence", [
        "It's not a caching problem, it's a schema problem.",
        "The bottleneck isn't the disk, it's the lock contention.",
        "This is not just a refactor but a rewrite.",
        "It is not only slower but also harder to read.",
        "You spotted the leak, and that's not nothing.",
        "That is not a bug but a missing guard.",
    ])
    def test_constructions_flagged(self, analyze_module, sentence):
        result = analyze_module.analyze_text(sentence)
        assert any("Negative parallelism" in i for i in _issues_of(result)), (
            f"not flagged: {sentence!r}"
        )

    @pytest.mark.parametrize("sentence", [
        "I did not fix it yesterday.",
        "The cache is not enabled on staging.",
        # Concessive "but": a new clause, not an alternative predicate.
        "The build is not reproducible but we ship it anyway.",
    ])
    def test_plain_negation_not_flagged(self, analyze_module, sentence):
        result = analyze_module.analyze_text(sentence)
        assert not any("Negative parallelism" in i for i in _issues_of(result)), (
            f"false positive on: {sentence!r}"
        )


class TestDefensiveNegation:
    """Defensive tails that deny a weaker claim the reader never made."""

    @pytest.mark.parametrize("sentence", [
        "The test asserts elapsed time, not merely that an error came back.",
        "The guard must fail on a mutation, not merely succeed on a clean tree.",
        "It asserts on the engine's produced error, not just a config flag.",
        "Run the suite against the real API, not only the recorded fixtures.",
        "The assertions are load-bearing, not decorative.",
        "This is a required implementation detail, not an optional nicety.",
    ])
    def test_defensive_tails_flagged(self, analyze_module, sentence):
        result = analyze_module.analyze_text(sentence)
        assert any("Defensive negation" in i for i in _issues_of(result)), (
            f"not flagged: {sentence!r}"
        )

    @pytest.mark.parametrize("sentence", [
        # Restrictive negation with no trailing comma frame.
        "The runner does not merely warn on a failed gate.",
        "We did not just ship it without review.",
        # Resolves into "but", so negative parallelism owns this one.
        "This is not just a refactor, but a rewrite.",
        "The queue drains slowly, not because of the disk.",
    ])
    def test_non_defensive_negation_not_flagged(self, analyze_module, sentence):
        result = analyze_module.analyze_text(sentence)
        assert not any("Defensive negation" in i for i in _issues_of(result)), (
            f"false positive on: {sentence!r}"
        )

    def test_one_negation_frame_yields_one_issue(self, analyze_module):
        """A sentence both detectors match is reported once.

        ", not just" satisfies the defensive tail and "not just ... but"
        satisfies negative parallelism. The guard is control flow rather than
        a lookahead, so it holds regardless of what sits between them.
        """
        sentence = "The build passes, not just on my machine, but it's broken in CI."
        issues = _issues_of(analyze_module.analyze_text(sentence))
        assert any("Negative parallelism" in i for i in issues), issues
        assert not any("Defensive negation" in i for i in issues), issues

    def test_pathological_whitespace_completes_promptly(self, analyze_module):
        """Ambiguous quantifiers over the same run of spaces backtrack.

        Measured at 8.2s for 20k spaces before the article was given its own
        whitespace, so this fails loudly rather than hanging the caller.
        """
        text = "The check is required, not" + " " * 20000 + "optional."
        start = time.perf_counter()
        analyze_module.analyze_text(text)
        assert time.perf_counter() - start < 2.0


class TestSycophancy:
    """C4 — validation openers, curly and straight apostrophes alike."""

    @pytest.mark.parametrize("sentence", [
        "You're absolutely right, the migration order was wrong.",
        "You\u2019re absolutely right, the migration order was wrong.",
        "You are absolutely right, the migration order was wrong.",
        "You're right to call that out.",
        "Great question! The retry budget is per-host.",
        "That's a sharp insight about the queue depth.",
    ])
    def test_openers_flagged(self, analyze_module, sentence):
        result = analyze_module.analyze_text(sentence)
        assert any("Sycophantic opener" in i for i in _issues_of(result)), (
            f"not flagged: {sentence!r}"
        )

    @pytest.mark.parametrize("sentence", [
        "You right-shifted the deploy window by an hour.",
        "You will need the admin token for that endpoint.",
        # "right to left" is a direction, not a speech act.
        "You're right to left of the divider.",
    ])
    def test_ordinary_second_person_not_flagged(self, analyze_module, sentence):
        result = analyze_module.analyze_text(sentence)
        assert not any("Sycophantic opener" in i for i in _issues_of(result)), (
            f"false positive on: {sentence!r}"
        )

    @pytest.mark.parametrize("sentence", [
        "- You're absolutely right, the migration order was wrong.",
        "> You're absolutely right about that.",
        "**You're absolutely right**, the order was wrong.",
    ])
    def test_markdown_decorated_openers_flagged(self, analyze_module, sentence):
        """The consuming skill lints markdown, where openers carry list and
        emphasis prefixes."""
        result = analyze_module.analyze_text(sentence)
        assert any("Sycophantic opener" in i for i in _issues_of(result)), (
            f"not flagged: {sentence!r}"
        )


class TestThroatClearing:
    """C5 — metadiscourse preamble before the actual content."""

    @pytest.mark.parametrize("sentence", [
        "Let me be honest, the index was never used.",
        "To be clear, the job runs hourly.",
        "Here's the thing: the worker never acked.",
        "Let's unpack why the retry loop stalled.",
        "I need to be brutally honest about the timeline.",
    ])
    def test_preambles_flagged(self, analyze_module, sentence):
        result = analyze_module.analyze_text(sentence)
        assert any("Throat-clearing" in i for i in _issues_of(result)), (
            f"not flagged: {sentence!r}"
        )

    @pytest.mark.parametrize("sentence", [
        "The index was never used.",
        "I want to be clear-headed about this.",
        "To be fair to him, the spec was ambiguous.",
        "We need to be fair in the scheduling algorithm.",
        "The queue is designed to be fair.",
    ])
    def test_ordinary_use_not_flagged(self, analyze_module, sentence):
        result = analyze_module.analyze_text(sentence)
        assert not any("Throat-clearing" in i for i in _issues_of(result)), (
            f"false positive on: {sentence!r}"
        )


class TestDecisiveness:
    """C11 — "decisive" importance-inflation frames, without flagging the
    ordinary military, sports and character senses of the adjective."""

    @pytest.mark.parametrize("sentence", [
        "The cache warm-up proved decisive for the launch.",
        "That review proves decisive in every incident retro.",
        "Latency was decisive in choosing the region.",
        "Automation played a decisive role in the migration.",
        "The decisive factor was the connection pool size.",
        "This marked a decisive shift in how the team ships.",
        "The outage gave the competitor a decisive advantage.",
        "Leaders must take decisive action on the backlog.",
        "The board needs to act decisively before renewal.",
        "Moving decisively, the team cut the release train.",
    ])
    def test_decisive_frames_flagged(self, analyze_module, sentence):
        result = analyze_module.analyze_text(sentence)
        assert any("Importance inflation" in i for i in _issues_of(result)), (
            f"not flagged: {sentence!r}"
        )

    @pytest.mark.parametrize("sentence", [
        "The Union won a decisive victory at Gettysburg.",
        "She is decisive under pressure and the team trusts her.",
        "The vote was decisive.",
        "He gave a decisive answer and hung up.",
        "Her decisive management style split the room.",
    ])
    def test_ordinary_decisive_not_flagged(self, analyze_module, sentence):
        result = analyze_module.analyze_text(sentence)
        assert not any("Importance inflation" in i for i in _issues_of(result)), (
            f"false positive on: {sentence!r}"
        )

    def test_decisive_counted_as_tier2(self, analyze_module):
        result = analyze_module.analyze_text(DECISIVE_TEXT)
        assert result["tier2_density"] > 0, (
            "decisive/decisively must count toward tier-2 density"
        )
        assert any("Tier-2" in i for i in _issues_of(result)), (
            "decisive clustered with its own frame must raise the tier-2 issue"
        )


class TestTier2CoOccurrence:
    """C6 — tier-2 words are too common to flag alone."""

    def test_tier2_alone_not_flagged(self, analyze_module):
        result = analyze_module.analyze_text(TIER2_ONLY_TEXT)
        assert result["tier2_density"] > 0, "metric must still count them"
        assert not any("Tier-2" in i for i in _issues_of(result)), (
            "tier-2 words alone must not raise an issue"
        )

    def test_tier2_with_other_signal_flagged(self, analyze_module):
        result = analyze_module.analyze_text(TIER2_WITH_SIGNAL_TEXT)
        assert any("Tier-2" in i for i in _issues_of(result)), (
            "tier-2 words must be flagged when clustered with another signal"
        )


class TestCommon10Density:
    """C7 — the Kobak common-10 set gets its own density metric."""

    def test_common10_density_reported(self, analyze_module):
        result = analyze_module.analyze_text(COMMON10_TEXT)
        assert result["kobak_common10_density"] > 0, result["kobak_common10_density"]

    def test_common10_absent_in_plain_text(self, analyze_module):
        result = analyze_module.analyze_text("The build broke at noon.")
        assert result["kobak_common10_density"] == 0


class TestEmDash:
    """C10 — house-style count, reported without an AI-like threshold."""

    def test_em_dash_counted(self, analyze_module):
        result = analyze_module.analyze_text(EM_DASH_TEXT)
        assert result["em_dash_count"] == 2

    def test_no_em_dash(self, analyze_module):
        result = analyze_module.analyze_text("The build broke at noon.")
        assert result["em_dash_count"] == 0


class TestSyntacticTemplates:
    """C8/C9 — POS n-gram templates (Shaib et al. arXiv:2407.00211)."""

    def test_templated_text_scores_higher_than_varied(self, analyze_module):
        templated = analyze_module.analyze_text(TEMPLATED_LONG_TEXT)
        varied = analyze_module.analyze_text(VARIED_LONG_TEXT)
        assert templated["syntactic_templates"] is not None
        assert varied["syntactic_templates"] is not None
        assert (
            templated["syntactic_templates"]["template_rate"]
            > varied["syntactic_templates"]["template_rate"]
        ), (
            f"templated={templated['syntactic_templates']['template_rate']} "
            f"varied={varied['syntactic_templates']['template_rate']}"
        )

    def test_no_duplicate_sentences_in_templated_fixture(self):
        """Guard: the fixture must not prove itself by verbatim repetition."""
        sentences = [s.strip() for s in TEMPLATED_LONG_TEXT.split(".") if s.strip()]
        assert len(sentences) == len(set(sentences)), "fixture repeats verbatim"

    def test_template_short_text_is_none(self, analyze_module):
        result = analyze_module.analyze_text(SINGLE_SENTENCE)
        assert result["syntactic_templates"] is None


class TestSpacySinglePass:
    """C13 — one spaCy invocation per analyzed input."""

    def test_spacy_single_pass(self, analyze_module, monkeypatch):
        calls = {"n": 0}
        real = analyze_module._nlp

        def counting(text):
            calls["n"] += 1
            return real(text)

        monkeypatch.setattr(analyze_module, "_nlp", counting)
        analyze_module.analyze_text(AI_TEXT)
        assert calls["n"] == 1, f"expected 1 spaCy call, got {calls['n']}"


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
                         "sentence_count", "word_count", "findings",
                         "hapax_ratio", "yules_k", "contraction_rate",
                         "signature_markers", "tier2_density",
                         "kobak_common10_density", "em_dash_count",
                         "syntactic_templates"}
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


class TestMissingDependencies:
    """C3-1 - a missing dependency stops the CLI with a banner and exit 3."""

    @pytest.mark.parametrize("module", ["spacy", "en_core_web_sm", "textstat", "lexicalrichness"])
    @pytest.mark.parametrize("mode", [["--json"], []], ids=["json", "human"])
    def test_banner_and_exit_3(self, tmp_path, module, mode):
        shim = tmp_path / module
        shim.mkdir()
        (shim / "__init__.py").write_text(f"raise ImportError('test shim: {module} removed')\n")
        env = dict(os.environ, PYTHONPATH=str(tmp_path))
        proc = subprocess.run(
            [sys.executable, TOOL, *mode],
            input=AI_TEXT, capture_output=True, text=True, timeout=60, env=env,
        )
        assert proc.returncode == 3, f"stdout: {proc.stdout[:200]!r} stderr: {proc.stderr!r}"
        assert proc.stdout == ""
        assert module in proc.stderr
        assert "test shim" in proc.stderr
        assert "brew install uv" in proc.stderr
        assert "python -m spacy download en_core_web_sm" in proc.stderr
        assert len(proc.stderr.strip().splitlines()) >= 4


# ---------------------------------------------------------------------------
# Wrapper integration tests (tools/slopometer)
# ---------------------------------------------------------------------------

import os
import shutil

WRAPPER = str(Path(__file__).parent / "slopometer")


def _path_without(binary: str) -> str:
    """Return a PATH string with directories containing `binary` removed."""
    keep = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(entry, binary)
        if not (os.path.isfile(candidate) and os.access(candidate, os.X_OK)):
            keep.append(entry)
    return os.pathsep.join(keep)


def _python3_has_deps(env: dict) -> bool:
    probe = "import spacy, textstat, lexicalrichness; spacy.load('en_core_web_sm')"
    return subprocess.run(
        ["python3", "-c", probe], env=env, capture_output=True, timeout=120,
    ).returncode == 0


@pytest.mark.parametrize(
    "scenario,expected_runner,skip_if_missing",
    [
        ("uv", "runner=uv", "uv"),
        ("python3-fallback", "runner=python3", "python3"),
    ],
)
class TestWrapper:
    """slopometer wrapper: prefers uv, falls back to python3."""

    def test_emits_valid_json(self, scenario, expected_runner, skip_if_missing):
        if shutil.which(skip_if_missing) is None:
            pytest.skip(f"{skip_if_missing} not available")

        env = {"HOME": os.environ.get("HOME", "/tmp"),
               "TMPDIR": os.environ.get("TMPDIR", "/tmp")}
        if scenario == "uv":
            env["PATH"] = os.environ["PATH"]
        else:
            env["PATH"] = _path_without("uv")

        proc = subprocess.run(
            [WRAPPER, "--json"],
            input=AI_TEXT, capture_output=True, text=True,
            timeout=300, env=env,
        )
        assert expected_runner in proc.stderr, f"stderr was: {proc.stderr!r}"
        # C3-3: the python3 path has no degraded mode. This machine's
        # Homebrew python3 lacks spaCy, so the banner branch is the one it hits.
        if scenario == "python3-fallback":
            assert "required" in proc.stderr, f"stderr was: {proc.stderr!r}"
            if not _python3_has_deps(env):
                assert proc.returncode == 3, f"stderr: {proc.stderr}"
                assert proc.stdout == ""
                assert "REQUIRED DEPENDENCIES MISSING" in proc.stderr
                return
        assert proc.returncode == 0, f"stderr: {proc.stderr}"
        data = json.loads(proc.stdout)
        assert "burstiness" in data
        assert "findings" in data
        assert data["word_count"] > 0
        # C11 names tools/slopometer as the boundary, so the new keys must be
        # asserted here and not only through analyze.py directly.
        new_keys = {"signature_markers", "tier2_density", "kobak_common10_density",
                    "em_dash_count", "syntactic_templates"}
        assert new_keys.issubset(data.keys()), f"missing: {new_keys - data.keys()}"


def test_wrapper_emits_clarity_and_visual_keys():
    if shutil.which("uv") is None and shutil.which("python3") is None:
        pytest.skip("no wrapper runner available")

    proc = subprocess.run(
        [WRAPPER, "--json"],
        input=AI_TEXT, capture_output=True, text=True, timeout=300,
    )
    assert proc.returncode == 0, f"stderr: {proc.stderr}"
    data = json.loads(proc.stdout)
    new_keys = {
        "long_sentence_count", "plain_swap_count", "nominalization_density",
        "mean_dependency_distance", "smog_index", "dale_chall_score",
        "difficult_word_rate", "visual_findings", "bold_density",
    }
    assert new_keys.issubset(data.keys()), f"missing: {new_keys - data.keys()}"


def test_wrapper_no_runners_exits_nonzero(tmp_path):
    """If neither uv nor python3 is on PATH, wrapper exits with hint."""
    # /bin and /usr/bin are needed so `env bash` works, but must not contain
    # python3 or uv. macOS /usr/bin ships python3, so skip if we can't isolate.
    minimal = os.pathsep.join(
        p for p in ["/bin", "/usr/bin"]
        if not (os.path.isfile(os.path.join(p, "python3"))
                or os.path.isfile(os.path.join(p, "uv")))
    )
    if not minimal or shutil.which("bash", path=minimal) is None:
        pytest.skip("cannot construct a PATH with bash but without python3/uv")
    env = {"PATH": minimal, "HOME": os.environ.get("HOME", "/tmp")}
    proc = subprocess.run(
        [WRAPPER, "--json"],
        input="hi", capture_output=True, text=True, timeout=30, env=env,
    )
    assert proc.returncode != 0
    assert "uv" in proc.stderr.lower() or "python" in proc.stderr.lower()
