# Design Notes

Deeper rationale behind the choices summarized in the README. Written to be the kind of
document you'd defend in a technical interview.

## Why rubric-governed scoring at all

Unstructured "LLM-as-judge, give it a 1–10" has two failure modes: the score is a black
box (you can't say *why* something failed), and it drifts (the same output scores
differently across runs and reviewers). Decomposing into named dimensions with written
definitions attacks both — each dimension is separately inspectable, and the definitions
are a shared, versioned contract rather than an implicit prompt.

## Why safety is a hard gate, not a weighted dimension

This is the load-bearing decision. Consider an output that is accurate, well-formatted,
logically sound, and efficient — but contains a hardcoded secret. Under a weighted scheme
with, say, a 0.15 safety weight, four strong dimensions can pull the aggregate above
threshold and the unsafe output **ships**. A hard gate makes the safety verdict
non-negotiable: it is evaluated first, and a failure returns immediately with
`aggregate = None`. The aggregate is never even computed. `test_safety_gate_blocks_even_perfect_scores`
encodes exactly this: all four dimensions at 1.0, safety false, result is rejection.

## Why the `Judge` Protocol is the center of the design

The evaluation logic (`evaluate`) is the part with real behavior worth testing — the
gate, the weighting, the threshold. If that logic called an LLM directly, testing it would
require API calls: slow, nondeterministic, costly, and flaky in CI. By depending only on
the `Judge` Protocol, `evaluate` can be driven by a `MockJudge` that returns exact scores,
so every scenario is deterministic and offline. The real `LLMJudge` is then just an
adapter, and swapping providers touches one method — any OpenAI-compatible
endpoint works by setting a base URL.

This is dependency inversion: the core logic depends on an abstraction, and both the real
and mock scorers depend on that same abstraction.

## Why the LLM SDK is an optional dependency

A reviewer cloning the repo should be able to run the tests and the offline demo in under
a minute without signing up for anything. Making the LLM SDK an optional extra
means `pip install -e ".[dev]"` pulls only pydantic, pyyaml, pytest, and ruff. The judge
imports its SDK lazily inside the call, so importing the package never requires an SDK.

## Why rubric weights are validated on load

The weighted aggregate is only meaningful if the weights form a proper convex combination
(sum to 1.0). A rubric where they sum to 0.8 would silently produce aggregates that can
never reach a 0.8 threshold even for perfect outputs. The Pydantic validator turns that
latent bug into a loud, immediate error with a message that explains the invariant —
including that safety is deliberately excluded from the sum because it is a gate.

## Scope and honesty

This is a demonstrator of a pattern, built from scratch for a portfolio. It is not a
reproduction of any proprietary system, and it intentionally keeps the surface small:
the goal is to show clear engineering judgment (validation, testability, separation of
concerns, honest docs), not feature breadth. The "What I'd build next" section names the
natural extensions — calibration against human labels, inter-judge agreement, regression
gating — which are where a production version would go.
