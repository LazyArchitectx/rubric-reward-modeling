"""The core evaluation loop.

This is the heart of the project and the part worth reading closely:

    1. The judge scores the output.
    2. SAFETY HARD GATE: if safety fails, the output is rejected immediately —
       before any aggregate is computed. A weighted safety term would let a
       high-scoring-but-unsafe output average its way to a pass; a hard gate
       makes that impossible.
    3. Otherwise, compute the weighted aggregate over the non-safety dimensions.
    4. Ship if the aggregate meets the threshold; otherwise route to rework.

It depends only on the `Judge` Protocol, so it is fully unit-testable offline.
"""

from __future__ import annotations

from rubric_eval.judge import Judge
from rubric_eval.schema import Decision, Rubric


def evaluate(output: str, rubric: Rubric, judge: Judge) -> Decision:
    result = judge.score(output, rubric)

    # (2) Safety hard gate — returns before the aggregate is ever computed.
    if not result.safety_pass:
        return Decision(ship=False, aggregate=None, reason="safety_gate", result=result)

    # (3) Weighted aggregate over the scored dimensions.
    aggregate = sum(
        result.dimension_scores[dim].score * rubric.weight(dim)
        for dim in rubric.weighted_dims
    )

    # (4) Threshold decision.
    ship = aggregate >= rubric.threshold
    reason = "passed" if ship else "below_threshold"
    return Decision(ship=ship, aggregate=round(aggregate, 4), reason=reason, result=result)
