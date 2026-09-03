"""The tests that matter: they prove the evaluation logic, not the model.

Every scenario is constructed deterministically with MockJudge(fixed_scores=...),
so these run offline with no API key and assert exact behavior.
"""

from rubric_eval.evaluator import evaluate
from rubric_eval.mock_judge import MockJudge
from rubric_eval.rubric import load_rubric

RUBRIC = load_rubric("config/rubric.yaml")
ALL_DIMS = {"accuracy": 1.0, "logic": 1.0, "formatting": 1.0, "efficiency": 1.0}


def test_safety_gate_blocks_even_perfect_scores():
    """A safety failure rejects the output even when every dimension is 1.0."""
    judge = MockJudge(fixed_scores=ALL_DIMS, safety_pass=False)
    decision = evaluate("perfect but unsafe", RUBRIC, judge)
    assert decision.ship is False
    assert decision.reason == "safety_gate"
    assert decision.aggregate is None  # gate returns BEFORE any aggregate is computed


def test_above_threshold_ships():
    judge = MockJudge(fixed_scores={d: 0.9 for d in RUBRIC.weighted_dims}, safety_pass=True)
    decision = evaluate("good output", RUBRIC, judge)
    assert decision.ship is True
    assert decision.reason == "passed"
    assert decision.aggregate == 0.9


def test_below_threshold_reworks():
    judge = MockJudge(fixed_scores={d: 0.5 for d in RUBRIC.weighted_dims}, safety_pass=True)
    decision = evaluate("mediocre output", RUBRIC, judge)
    assert decision.ship is False
    assert decision.reason == "below_threshold"


def test_weighted_aggregate_is_correct():
    """accuracy .35*1 + logic .30*0 + formatting .20*1 + efficiency .15*0 = 0.55"""
    judge = MockJudge(
        fixed_scores={"accuracy": 1.0, "logic": 0.0, "formatting": 1.0, "efficiency": 0.0},
        safety_pass=True,
    )
    decision = evaluate("mixed output", RUBRIC, judge)
    assert abs(decision.aggregate - 0.55) < 1e-6
    assert decision.ship is False  # 0.55 < 0.80 threshold


def test_exact_threshold_ships():
    """A score exactly at the threshold ships (>= is inclusive)."""
    judge = MockJudge(fixed_scores={d: 0.80 for d in RUBRIC.weighted_dims}, safety_pass=True)
    decision = evaluate("borderline", RUBRIC, judge)
    assert decision.ship is True


def test_offline_deny_list_trips_safety():
    """The heuristic mock still fires the gate on an obvious hardcoded secret."""
    judge = MockJudge()  # heuristic mode, safety_pass defaults True
    decision = evaluate("api_key = 'sk-live-1234'", RUBRIC, judge)
    assert decision.result.safety_pass is False
    assert decision.ship is False
