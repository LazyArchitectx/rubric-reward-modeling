"""A deterministic judge for tests and offline demos — no API key required.

Two modes:
  * fixed_scores: return exactly the scores you specify (used by unit tests to
    construct precise scenarios — e.g. "all 1.0 but safety fails").
  * heuristic (default): a transparent, predictable stand-in so `--mock` on the CLI
    produces sensible output offline. Not a real evaluator — a demo aid.
"""

from __future__ import annotations

from rubric_eval.schema import DimensionScore, JudgeResult, Rubric

# A simple deny-list so the offline demo can still show the safety gate firing.
_UNSAFE_MARKERS = ("hardcoded_secret", "api_key =", "sk-", "password =")


class MockJudge:
    def __init__(
        self,
        fixed_scores: dict[str, float] | None = None,
        safety_pass: bool = True,
    ) -> None:
        self.fixed_scores = fixed_scores
        self.safety_pass = safety_pass

    def score(self, output: str, rubric: Rubric) -> JudgeResult:
        if self.fixed_scores is not None:
            scores = {
                dim: DimensionScore(
                    score=self.fixed_scores.get(dim, 0.5), rationale="fixed"
                )
                for dim in rubric.weighted_dims
            }
        else:
            base = min(1.0, len(output) / 200)  # transparent heuristic (demo only)
            scores = {
                dim: DimensionScore(score=round(base, 3), rationale="heuristic")
                for dim in rubric.weighted_dims
            }

        unsafe = any(marker in output.lower() for marker in _UNSAFE_MARKERS)
        return JudgeResult(
            dimension_scores=scores,
            safety_pass=self.safety_pass and not unsafe,
            safety_rationale="mock verdict",
        )
