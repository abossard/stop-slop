# Evals

`copilot_eval.py` runs the skill through GitHub Copilot CLI on writing tasks and compares versions. Each case in `evals.json` comes from a real correction the owner made to an agent's writing. The fixtures in `files/<case>/` are synthetic copies of those situations.

Each run starts Copilot in a temporary directory with a fresh `COPILOT_HOME`, so installed plugins and personal instructions stay out. The skill under test is loaded with `--plugin-dir`.

## Run

```bash
evals/copilot_eval.py run --iteration evals/workspace/iteration-N \
  --config new_skill=. --config old_skill=git:main --config without_skill=none --runs 2
evals/copilot_eval.py grade --iteration evals/workspace/iteration-N
evals/copilot_eval.py compare --iteration evals/workspace/iteration-N --a new_skill --b old_skill
```

A config is `none`, `.` (the working tree), `git:<ref>` or a plugin directory. `--evals a,b` limits the cases; `--model` sets the writer model (default `gpt-6.1-sol`) and `--judge-model` the grader (default `claude-sonnet-5.5`). Finished runs are skipped, so an interrupted command can be rerun.

## Grading

- `grade` runs deterministic checks on the deliverable: no em dashes, no mention of the skill or its metrics, the case's word ceiling, required facts and forbidden patterns. It also runs the slopometer and asks the judge model about each case's `expectations`. For in-place edits (`grade_added_only`), only the text the agent added is graded.
- `compare` shows a judge two deliverables for the same case in random order and asks which one a senior reader would rather receive. It writes the win rate to `compare-<a>-vs-<b>.json`.
- `slop_summary.md` lists per config: pass rate, slopometer flag rate, words, how often the skill loaded, slopometer calls, seconds and tokens.

The layout matches skill-creator, so its viewer and benchmark scripts read the results:

```bash
python -m scripts.aggregate_benchmark evals/workspace/iteration-N --skill-name stop-slop
python eval-viewer/generate_review.py evals/workspace/iteration-N --benchmark evals/workspace/iteration-N/benchmark.json
```

Run both from the skill-creator directory. A writer run costs one premium request (`usage.json` records it); grading and comparing add one judge prompt per run.
