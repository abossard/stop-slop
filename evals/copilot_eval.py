#!/usr/bin/env python3
"""Run, grade and compare stop-slop evals through GitHub Copilot CLI.

Layout (compatible with skill-creator's aggregate_benchmark.py and eval viewer):
  <iteration>/plugins/<config>/                      plugin snapshot per config
  <iteration>/eval-<name>/eval_metadata.json
  <iteration>/eval-<name>/<config>/run-<n>/outputs/  reply.md and files the agent wrote
  <iteration>/eval-<name>/<config>/run-<n>/{events.jsonl,usage.json,metrics.json,timing.json,grading.json}

Usage:
  evals/copilot_eval.py run --iteration DIR --config new_skill=. --config old_skill=git:main \
      --config without_skill=none [--runs 2] [--model gpt-6.1-sol] [--evals name,...]
  evals/copilot_eval.py grade --iteration DIR [--judge-model claude-sonnet-5.5]
  evals/copilot_eval.py compare --iteration DIR --a new_skill --b old_skill

Each run uses a fresh COPILOT_HOME, so only the plugin passed with --plugin-dir is loaded.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import difflib
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EVALS_FILE = REPO / "evals" / "evals.json"
FIXTURES = REPO / "evals" / "files"
SLOPOMETER = REPO / "tools" / "slopometer"
PLUGIN_PARTS = [".claude-plugin", "skills", "references", "tools"]
IGNORE = shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc", "test_*.py")
RUN_TIMEOUT = 900


def load_evals(only: str | None) -> list[dict]:
    evals = json.loads(EVALS_FILE.read_text())["evals"]
    if only:
        wanted = set(only.split(","))
        evals = [e for e in evals if e["name"] in wanted]
    return evals


# --- copilot invocation -----------------------------------------------------


def copilot(prompt: str, workdir: Path, model: str, plugin: Path | None,
            events_path: Path | None = None, usage_path: Path | None = None,
            silent: bool = False) -> subprocess.CompletedProcess:
    home = Path(tempfile.mkdtemp(prefix="cphome-"))
    cmd = ["copilot", "-p", prompt, "--model", model, "--allow-all-tools",
           "--no-custom-instructions", "--no-auto-update", "--no-ask-user",
           "--disable-builtin-mcps", "-C", str(workdir)]
    cmd += ["-s"] if silent else ["--output-format", "json"]
    if usage_path:
        cmd += ["--usage-output-file", str(usage_path)]
    if plugin:
        cmd += ["--plugin-dir", str(plugin), "--add-dir", str(plugin)]
    try:
        proc = subprocess.run(cmd, env={**os.environ, "COPILOT_HOME": str(home)},
                              capture_output=True, text=True, timeout=RUN_TIMEOUT)
    finally:
        shutil.rmtree(home, ignore_errors=True)
    if events_path:
        events_path.write_text(proc.stdout)
    return proc


# --- run --------------------------------------------------------------------


def snapshot_plugin(source: str, dest: Path) -> Path | None:
    """Materialize a plugin config: 'none', '.', 'git:<ref>' or a directory."""
    if source == "none":
        return None
    if dest.exists():
        return dest
    dest.mkdir(parents=True)
    if source.startswith("git:"):
        archive = subprocess.run(["git", "-C", str(REPO), "archive", source[4:], *PLUGIN_PARTS],
                                 capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)
        for test in dest.glob("tools/test_*.py"):
            test.unlink()
        return dest
    root = REPO if source == "." else Path(source).resolve()
    for part in PLUGIN_PARTS:
        if (root / part).exists():
            shutil.copytree(root / part, dest / part, ignore=IGNORE)
    return dest


def tree_hashes(root: Path) -> dict[str, str]:
    out = {}
    for p in root.rglob("*"):
        if p.is_file() and ".git" not in p.relative_to(root).parts:
            out[str(p.relative_to(root))] = hashlib.sha1(p.read_bytes()).hexdigest()
    return out


def prepare_workdir(ev: dict) -> Path:
    work = Path(tempfile.mkdtemp(prefix=f"slop-{ev['name']}-"))
    src = FIXTURES / ev["name"]
    if src.is_dir():
        shutil.copytree(src, work, dirs_exist_ok=True)
    setup = work / "setup.sh"
    if setup.exists():
        subprocess.run(["bash", "setup.sh"], cwd=work, check=True, capture_output=True)
        setup.unlink()
    return work


def summarize_events(events_text: str) -> dict:
    tools, replies, skill_invoked, slopometer_runs, errors = {}, [], False, 0, 0
    for line in events_text.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        data = ev.get("data") or {}
        if ev.get("type") == "tool.execution_start":
            name = data.get("toolName", "?")
            tools[name] = tools.get(name, 0) + 1
            args = data.get("arguments") or {}
            if name == "skill" and args.get("skill") == "stop-slop":
                skill_invoked = True
            if re.search(r"slopometer|analyze\.py", json.dumps(args)):
                slopometer_runs += 1
        elif ev.get("type") == "tool.execution_complete" and data.get("success") is False:
            errors += 1
        elif ev.get("type") == "assistant.message" and not data.get("parentToolCallId"):
            if data.get("content"):
                replies.append(data["content"])
    return {"tool_calls": tools, "total_tool_calls": sum(tools.values()), "skill_invoked": skill_invoked,
            "slopometer_runs": slopometer_runs, "errors_encountered": errors,
            "reply": replies[-1] if replies else ""}


def run_one(ev: dict, config: str, plugin: Path | None, n: int, iteration: Path, model: str) -> str:
    run_dir = iteration / f"eval-{ev['name']}" / config / f"run-{n}"
    if (run_dir / "timing.json").exists():
        return f"skip {run_dir.relative_to(iteration)}"
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    work = prepare_workdir(ev)
    before = tree_hashes(work)
    start = time.time()
    proc = copilot(ev["prompt"], work, model, plugin, run_dir / "events.jsonl", run_dir / "usage.json")
    duration = time.time() - start
    summary = summarize_events(proc.stdout)
    (outputs / "reply.md").write_text(summary.pop("reply"))
    after = tree_hashes(work)
    changed = sorted(p for p, h in after.items() if before.get(p) != h)
    for rel in changed:
        dest = outputs / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(work / rel, dest)
    shutil.rmtree(work, ignore_errors=True)
    usage = {}
    if (run_dir / "usage.json").exists():
        usage = json.loads((run_dir / "usage.json").read_text())
    tokens = sum(m["usage"]["inputTokens"] + m["usage"]["outputTokens"]
                 for m in usage.get("modelMetrics", {}).values())
    metrics = {**summary, "files_created": changed, "exit_code": proc.returncode,
               "stderr_tail": proc.stderr[-2000:], "model": model}
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (run_dir / "timing.json").write_text(json.dumps(
        {"total_tokens": tokens, "duration_ms": int(duration * 1000),
         "total_duration_seconds": round(duration, 1)}, indent=2))
    flag = "skill" if summary["skill_invoked"] else "-"
    return f"done {run_dir.relative_to(iteration)} {duration:.0f}s {flag} exit={proc.returncode}"


def check_frontmatter(plugin: Path) -> None:
    """Copilot silently skips a skill whose frontmatter is not valid YAML; catch the common case."""
    for skill in plugin.glob("skills/*/SKILL.md"):
        header = skill.read_text().split("---")[1]
        for line in header.strip().splitlines():
            key, _, value = line.partition(":")
            value = value.strip()
            if value and value[0] not in "\"'|>" and ": " in value:
                sys.exit(f"{skill}: unquoted ': ' in '{key}' makes the frontmatter invalid YAML")


def cmd_run(args) -> None:
    iteration = Path(args.iteration).resolve()
    evals = load_evals(args.evals)
    configs = {}
    for spec in args.config:
        name, source = spec.split("=", 1)
        configs[name] = snapshot_plugin(source, iteration / "plugins" / name)
        if configs[name]:
            check_frontmatter(configs[name])
    for i, ev in enumerate(evals):
        meta = {"eval_id": i, "eval_name": ev["name"], "prompt": ev["prompt"],
                "assertions": ev.get("expectations", [])}
        d = iteration / f"eval-{ev['name']}"
        # the benchmark script reads it from the eval dir, the viewer from the config dir
        for target in [d, *(d / c for c in configs)]:
            target.mkdir(parents=True, exist_ok=True)
            (target / "eval_metadata.json").write_text(json.dumps(meta, indent=2))
    jobs = [(ev, c, p, n) for n in range(1, args.runs + 1) for ev in evals for c, p in configs.items()]
    with cf.ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = [pool.submit(run_one, ev, c, p, n, iteration, args.model) for ev, c, p, n in jobs]
        for f in cf.as_completed(futures):
            print(f.result(), flush=True)


# --- grade ------------------------------------------------------------------


def added_text(original: str, edited: str) -> str:
    """What the agent wrote: inserted lines, and inserted words inside changed lines."""
    old, new = original.splitlines(), edited.splitlines()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if op == "insert":
            out.extend(new[j1:j2])
        elif op == "replace":
            old_words, new_words = " ".join(old[i1:i2]).split(), " ".join(new[j1:j2]).split()
            words = difflib.SequenceMatcher(None, old_words, new_words, autojunk=False)
            out.extend(" ".join(new_words[b1:b2]) for tag, _, _, b1, b2 in words.get_opcodes()
                       if tag in ("insert", "replace"))
    return "\n".join(out)


def deliverable(ev: dict, run_dir: Path) -> tuple[str, str]:
    """The text to grade: the deliverable file (only its added lines for in-place edits) or the reply."""
    outputs = run_dir / "outputs"
    matches = sorted(outputs.glob(ev["deliverable"])) if ev.get("deliverable") else []
    if not matches:
        return "reply.md", (outputs / "reply.md").read_text()
    path = matches[0]
    rel = str(path.relative_to(outputs))
    text = path.read_text()
    original = FIXTURES / ev["name"] / rel
    if ev.get("grade_added_only") and original.exists():
        return f"{rel} (added lines)", added_text(original.read_text(), text)
    return rel, text


def slopometer(text: str) -> dict:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(text)
    proc = subprocess.run([str(SLOPOMETER), "--json", "--file", fh.name], capture_output=True, text=True)
    os.unlink(fh.name)
    if proc.returncode != 0:
        return {"error": proc.stderr[-500:]}
    data = json.loads(proc.stdout)
    flagged = len(data.get("findings", []))
    sentences = data.get("sentence_count") or 1
    return {"flagged_sentences": flagged, "sentence_count": sentences,
            "flag_rate": round(flagged / sentences, 3),
            "issues": sum(len(f.get("issues", [])) for f in data.get("findings", [])),
            "visual_findings": len(data.get("visual_findings", [])),
            "word_count": data.get("word_count"), "em_dash_count": data.get("em_dash_count", 0),
            "ai_vocabulary_density": data.get("ai_vocabulary_density")}


COMMENT_LINE = re.compile(r"^\s*(//|/\*|\*|#(?!!))")
MIN_WORDS_FOR_FLAG_RATE = 100  # below this, one flagged sentence swings the rate past any threshold
PROCESS_LEAK = re.compile(r"stop-slop|slopometer|burstiness|ai_vocabulary|\b\d{2}/60\b", re.I)


def deterministic_checks(ev: dict, text: str, slop: dict, reply: str) -> list[dict]:
    checks = ev.get("checks", {})
    words = len(text.split())
    leak = PROCESS_LEAK.search(text)
    results = [{"text": "No em dashes", "passed": "—" not in text,
                "evidence": f"{text.count(chr(0x2014))} em dashes"},
               {"text": "Does not mention the skill, the analyzer or its scores", "passed": not leak,
                "evidence": leak.group(0) if leak else "absent"}]
    if "max_words" in checks:
        results.append({"text": f"At most {checks['max_words']} words", "passed": words <= checks["max_words"],
                        "evidence": f"{words} words"})
    if "reply_max_words" in checks:
        n = len(reply.split())
        results.append({"text": f"Chat reply at most {checks['reply_max_words']} words",
                        "passed": n <= checks["reply_max_words"], "evidence": f"{n} words"})
    if "max_comment_lines" in checks:
        n = sum(bool(COMMENT_LINE.match(line)) for line in text.splitlines())
        results.append({"text": f"At most {checks['max_comment_lines']} new comment lines",
                        "passed": n <= checks["max_comment_lines"], "evidence": f"{n} comment lines"})
    if "error" not in slop and words >= MIN_WORDS_FOR_FLAG_RATE:
        limit = checks.get("max_flag_rate", 0.25)
        results.append({"text": f"Slopometer flags at most {int(limit * 100)}% of sentences",
                        "passed": slop["flag_rate"] <= limit,
                        "evidence": f"{slop['flagged_sentences']}/{slop['sentence_count']} sentences flagged"})
    for item in checks.get("must_include", []):
        hit = re.search(item["pattern"], text, re.I | re.S)
        results.append({"text": f"Keeps: {item['label']}", "passed": bool(hit),
                        "evidence": hit.group(0)[:120] if hit else "not found"})
    for item in checks.get("must_not", []):
        hit = re.search(item["pattern"], text, re.I | re.S)
        results.append({"text": f"Avoids: {item['label']}", "passed": not hit,
                        "evidence": hit.group(0)[:120] if hit else "absent"})
    return results


JUDGE_PROMPT = """You grade one writing sample against a list of expectations. Do not use any tools.

TASK GIVEN TO THE WRITER:
<task>
{task}
</task>

{original}WRITER'S DELIVERABLE ({name}):
<deliverable>
{text}
</deliverable>

EXPECTATIONS:
{expectations}

For each expectation decide passed true/false. Be strict: pass only with clear evidence in the deliverable.
Quote the deciding text (max 25 words) as evidence.
Answer with only a JSON array, one object per expectation, in order:
[{{"text": "<expectation>", "passed": true, "evidence": "..."}}]"""


def extract_json(raw: str, opener: str):
    start, end = raw.find(opener), raw.rfind("]" if opener == "[" else "}")
    if start < 0 or end < start:
        raise ValueError(f"no JSON in judge output: {raw[:300]}")
    return json.loads(raw[start:end + 1])


def original_context(ev: dict) -> str:
    """The fixture file the writer edited, so the judge can compare against it."""
    if not ev.get("deliverable") or "*" in ev["deliverable"]:
        return ""
    path = FIXTURES / ev["name"] / ev["deliverable"]
    if not path.exists():
        return ""
    return f"FILE BEFORE THE WRITER EDITED IT ({ev['deliverable']}):\n<original>\n{path.read_text()[:8000]}\n</original>\n\n"


def judge_expectations(ev: dict, name: str, text: str, model: str) -> list[dict]:
    expectations = ev.get("expectations", [])
    if not expectations:
        return []
    prompt = JUDGE_PROMPT.format(task=ev["prompt"], name=name, text=text, original=original_context(ev),
                                 expectations="\n".join(f"{i + 1}. {e}" for i, e in enumerate(expectations)))
    work = Path(tempfile.mkdtemp(prefix="judge-"))
    for attempt in range(2):
        proc = copilot(prompt, work, model, None, silent=True)
        try:
            verdicts = extract_json(proc.stdout, "[")
            break
        except ValueError as err:
            if attempt:
                verdicts = [{"text": e, "passed": False, "evidence": f"judge error: {err}"} for e in expectations]
    shutil.rmtree(work, ignore_errors=True)
    for v, e in zip(verdicts, expectations):
        v["text"] = e
    return verdicts


def grade_run(ev: dict, run_dir: Path, judge_model: str, refresh_checks: bool = False) -> str:
    existing = run_dir / "grading.json"
    if existing.exists() and not refresh_checks:
        return f"skip {run_dir}"
    name, text = deliverable(ev, run_dir)
    reply = (run_dir / "outputs" / "reply.md").read_text()
    slop = slopometer(text) if text.strip() else {"error": "empty deliverable"}
    if existing.exists():
        judged = [r for r in json.loads(existing.read_text())["expectations"] if r["text"] in ev.get("expectations", [])]
    else:
        judged = judge_expectations(ev, name, text, judge_model)
    results = deterministic_checks(ev, text, slop, reply) + judged
    passed = sum(r["passed"] for r in results)
    metrics = json.loads((run_dir / "metrics.json").read_text())
    timing = json.loads((run_dir / "timing.json").read_text())
    grading = {
        "expectations": results,
        "summary": {"passed": passed, "failed": len(results) - passed, "total": len(results),
                    "pass_rate": round(passed / len(results), 3) if results else 0.0},
        "execution_metrics": {"tool_calls": metrics["tool_calls"], "total_tool_calls": metrics["total_tool_calls"],
                              "errors_encountered": metrics["errors_encountered"], "output_chars": len(text)},
        "timing": timing,
        "slop_metrics": {**slop, "deliverable": name, "words": len(text.split()),
                         "skill_invoked": metrics["skill_invoked"], "slopometer_runs": metrics["slopometer_runs"]},
    }
    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2))
    return f"graded {run_dir.parent.parent.name}/{run_dir.parent.name}/{run_dir.name} {passed}/{len(results)}"


def run_dirs(iteration: Path, evals: list[dict]):
    for ev in evals:
        for run_dir in sorted((iteration / f"eval-{ev['name']}").glob("*/run-*")):
            if (run_dir / "timing.json").exists():
                yield ev, run_dir


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 3) if xs else None


def write_summary(iteration: Path, evals: list[dict]) -> None:
    rows = {}
    for ev, run_dir in run_dirs(iteration, evals):
        g = json.loads((run_dir / "grading.json").read_text())
        rows.setdefault(run_dir.parent.name, []).append(g)
    lines = ["| Config | Pass rate | Flag rate | Words | Skill invoked | Slopometer runs | Seconds | Tokens |",
             "|---|---|---|---|---|---|---|---|"]
    for config, gs in sorted(rows.items()):
        sm = [g["slop_metrics"] for g in gs]
        lines.append(" | ".join([
            f"| {config}", str(mean([g["summary"]["pass_rate"] for g in gs])),
            str(mean([s.get("flag_rate") for s in sm])), str(mean([s["words"] for s in sm])),
            str(mean([1.0 if s["skill_invoked"] else 0.0 for s in sm])), str(mean([s["slopometer_runs"] for s in sm])),
            str(mean([g["timing"]["total_duration_seconds"] for g in gs])),
            str(mean([g["timing"]["total_tokens"] for g in gs])) + " |"]))
    (iteration / "slop_summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def cmd_grade(args) -> None:
    iteration = Path(args.iteration).resolve()
    evals = load_evals(args.evals)
    with cf.ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = [pool.submit(grade_run, ev, rd, args.judge_model, args.refresh_checks)
                   for ev, rd in run_dirs(iteration, evals)]
        for f in cf.as_completed(futures):
            print(f.result(), flush=True)
    write_summary(iteration, evals)


# --- compare ----------------------------------------------------------------


COMPARE_PROMPT = """Two writers did the same task. Decide which deliverable the reader would rather receive.
Do not use any tools.

THE READER:
{reader}

Judge in this order:
1. Does it give the reader everything the task needs (facts, decisions, actions) without inventing facts?
2. Does it read like a competent human colleague: direct, specific, no filler, no AI-typical phrasing,
   no restating, no process narration, format and length fit the medium?
Shorter is better only when nothing needed is lost.

TASK:
<task>
{task}
</task>

{original}DELIVERABLE 1:
<d1>
{one}
</d1>

DELIVERABLE 2:
<d2>
{two}
</d2>

Answer with only JSON: {{"winner": "1" | "2" | "tie", "reason": "<max 30 words>"}}"""


GENERIC_READER = "A busy, senior reader."
READER_FILE = REPO / "evals" / "reader.md"


def compare_pair(ev: dict, a_dir: Path, b_dir: Path, model: str, rng: random.Random, reader: str) -> dict:
    _, a_text = deliverable(ev, a_dir)
    _, b_text = deliverable(ev, b_dir)
    swap = rng.random() < 0.5
    one, two = (b_text, a_text) if swap else (a_text, b_text)
    work = Path(tempfile.mkdtemp(prefix="cmp-"))
    proc = copilot(COMPARE_PROMPT.format(reader=reader, task=ev["prompt"], original=original_context(ev),
                                        one=one, two=two), work, model, None, silent=True)
    shutil.rmtree(work, ignore_errors=True)
    try:
        verdict = extract_json(proc.stdout, "{")
    except ValueError as err:
        return {"eval": ev["name"], "run": a_dir.name, "winner": "error", "reason": str(err)[:200]}
    w = verdict.get("winner")
    winner = "tie" if w == "tie" else ("a" if (w == "1") != swap else "b")
    return {"eval": ev["name"], "run": a_dir.name, "winner": winner, "reason": verdict.get("reason", "")}


def cmd_compare(args) -> None:
    iteration = Path(args.iteration).resolve()
    evals = load_evals(args.evals)
    rng = random.Random(args.seed)
    reader = GENERIC_READER if args.reader == "none" else Path(args.reader).read_text()
    pairs = []
    for ev in evals:
        for a_dir in sorted((iteration / f"eval-{ev['name']}" / args.a).glob("run-*")):
            b_dir = iteration / f"eval-{ev['name']}" / args.b / a_dir.name
            if (a_dir / "timing.json").exists() and (b_dir / "timing.json").exists():
                pairs.append((ev, a_dir, b_dir, random.Random(rng.random())))
    with cf.ThreadPoolExecutor(max_workers=args.parallel) as pool:
        results = list(pool.map(lambda p: compare_pair(p[0], p[1], p[2], args.judge_model, p[3], reader), pairs))
    tally = {k: sum(r["winner"] == k for r in results) for k in ("a", "b", "tie", "error")}
    decided = tally["a"] + tally["b"]
    out = {"a": args.a, "b": args.b, "judge_model": args.judge_model, "reader": args.reader, "tally": tally,
           "a_win_rate": round(tally["a"] / decided, 3) if decided else None, "results": results}
    suffix = "" if args.reader == "none" else f"-{Path(args.reader).stem}"
    (iteration / f"compare-{args.a}-vs-{args.b}{suffix}.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: out[k] for k in ("a", "b", "tally", "a_win_rate")}))
    for r in results:
        print(f"{r['eval']:<34} {r['run']}  {r['winner']:<5} {r['reason']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--iteration", required=True)
    common.add_argument("--evals", help="comma-separated eval names")
    common.add_argument("--parallel", type=int, default=4)
    common.add_argument("--judge-model", default="claude-sonnet-5.5")
    p_run = sub.add_parser("run", parents=[common])
    p_run.add_argument("--config", action="append", required=True, help="name=none|.|git:<ref>|<plugin dir>")
    p_run.add_argument("--runs", type=int, default=1)
    p_run.add_argument("--model", default="gpt-6.1-sol")
    p_grade = sub.add_parser("grade", parents=[common])
    p_grade.add_argument("--refresh-checks", action="store_true",
                         help="recompute deterministic checks on graded runs, keep judge verdicts")
    p_cmp = sub.add_parser("compare", parents=[common])
    p_cmp.add_argument("--a", required=True)
    p_cmp.add_argument("--b", required=True)
    p_cmp.add_argument("--seed", type=int, default=7)
    p_cmp.add_argument("--reader", default=str(READER_FILE),
                       help="file describing the reader the judge stands in for, or 'none' for a generic reader")
    args = parser.parse_args()
    {"run": cmd_run, "grade": cmd_grade, "compare": cmd_compare}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
