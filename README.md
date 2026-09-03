# Rubric-Governed LLM Evaluation

A small, tested system that turns *"is this a good model output?"* from a subjective
judgment into a **measurable, governed decision**: an LLM-as-judge scores each output
against a versioned rubric, a **safety hard-gate** can veto regardless of scores, and a
weighted aggregate is compared to a threshold to decide **ship vs. rework**.

[![ci](https://github.com/LazyArchitectx/rubric-reward-modeling/actions/workflows/ci.yml/badge.svg)](https://github.com/LazyArchitectx/rubric-reward-modeling/actions)

> **What this is.** A portfolio demonstrator of the *rubric-governed reward-modeling /
> LLM-as-judge* pattern — the approach behind automated grading and reward loops for
> LLM outputs. It is a clean, from-scratch implementation I built to show the pattern and
> the engineering around it. It is **not** a proprietary production system, and it ships
> no confidential code or data.

## Run it in the cloud (GitHub Codespaces)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/LazyArchitectx/rubric-reward-modeling)

No local setup. Click the badge (or **Code → Codespaces → Create codespace**) and the
environment auto-installs itself. Then, in the terminal:

```bash
rubric-eval score --file data/samples.jsonl --mock   # offline demo, no API key
pytest -v                                             # 15 tests, all offline
```


## The problem it solves

"Good output" usually lives in reviewers' heads — grading is subjective, inconsistent,
and doesn't scale. This project makes the definition **explicit and executable**:

- The rubric is a versioned config, not tribal knowledge.
- Scoring is reproducible and traceable to a specific rubric version.
- Safety can't be averaged away — it's a gate, not a weighted term.

## Architecture

```
   output ─►  Judge (LLM-as-judge)  ─►  per-dimension scores + safety verdict
                                              │
                    ┌─────────────────────────┤
                    ▼                          ▼
            safety FAILS                 safety PASSES
                    │                          │
                    ▼                          ▼
              REJECT (gate)      weighted aggregate ≥ threshold ?
              aggregate=None            ├─ yes ─► SHIP
                                        └─ no  ─► REWORK
```

The `Judge` is a **Protocol**. Everything downstream depends only on that interface, so
the evaluation logic is fully unit-testable against a deterministic `MockJudge` — no API
calls in the test suite. The real `LLMJudge` is one interchangeable
implementation.

## Key design decisions

| Decision | Why |
|---|---|
| **Safety is a hard gate, not a weighted score** | A weighted safety term lets a high-scoring but unsafe output average its way to a pass. The gate returns *before* the aggregate is computed, so that's impossible. |
| **Judge behind a `Protocol`** | The eval logic is testable offline with a mock; the LLM provider is swappable in one file. Tests prove the logic, not the model. |
| **LLM SDK is an optional dependency** | `pip install -e .` and the whole test suite run with **no API key**. You add a key only for the real judge. |
| **Rubric weights validated to sum to 1.0 on load** | A malformed rubric fails loudly with a clear error, not silently with wrong scores. |
| **Provider/model from env, not hardcoded** | Model names change; the repo shouldn't rot when they do. |

## Quickstart

```bash
pip install -e ".[dev]"

# Offline demo — no API key needed (uses the deterministic mock judge):
rubric-eval score --file data/samples.jsonl --mock
```

Sample offline output (note the 4th line — the safety gate firing on a hardcoded secret):

```json
{"ship": false, "reason": "below_threshold", "aggregate": 0.6, ...}
{"ship": false, "reason": "safety_gate", "aggregate": null, "safety_pass": false, ...}
```

Run with a **real LLM judge**:

```bash
cp .env.example .env          # add your key, pick a provider
pip install -e ".[llm]"
export $(grep -v '^#' .env | xargs)
rubric-eval score --input "def add(a, b): return a + b"
```

## Testing

```bash
ruff check .     # lint
pytest -v        # 15 tests, all offline (mock judge) — no key required
```

The tests that matter are in [`tests/test_evaluator.py`](tests/test_evaluator.py): they
prove the **safety gate**, the **threshold** boundary, and the **weighted aggregate** —
the actual decision logic — using deterministic fixtures.

## Project layout

```
config/rubric.yaml          the governing definition of "good" (5 dims, safety gate)
src/rubric_eval/
  schema.py                 Pydantic contracts (rubric, scores, decision)
  rubric.py                 load + validate the rubric
  judge.py                  Judge Protocol + LLM-as-judge + provider factory
  mock_judge.py             deterministic judge for tests / offline demo
  evaluator.py              the core loop: gate -> aggregate -> decision
  cli.py                    `rubric-eval score ...`
tests/                      schema, rubric, evaluator, and CLI tests
docs/DESIGN.md              deeper architecture + rationale
```

## What I'd build next

- Calibration report: judge scores vs. human labels, per dimension (agreement/κ).
- A second judge + inter-judge agreement, to bound single-judge variance.
- Batch mode with cost/latency tracking and a results dashboard.
- CI gate: fail the build if mean score on a golden set regresses.

## License

MIT — see [LICENSE](LICENSE).
