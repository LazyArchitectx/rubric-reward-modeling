"""Schema validation tests — the rubric contract fails loudly when wrong."""

import pytest
from pydantic import ValidationError

from rubric_eval.schema import Rubric


def _valid_rubric_dict():
    return {
        "version": "1.0.0",
        "threshold": 0.8,
        "dimensions": {
            "accuracy": {"weight": 0.5, "definition": "correct"},
            "logic": {"weight": 0.5, "definition": "sound"},
        },
        "safety": {"mode": "hard_gate", "definition": "safe"},
    }


def test_valid_rubric_loads():
    rubric = Rubric.model_validate(_valid_rubric_dict())
    assert rubric.version == "1.0.0"
    assert rubric.weighted_dims == ["accuracy", "logic"]
    assert rubric.weight("accuracy") == 0.5


def test_weights_must_sum_to_one():
    bad = _valid_rubric_dict()
    bad["dimensions"]["accuracy"]["weight"] = 0.9  # now sums to 1.4
    with pytest.raises(ValidationError, match="sum to 1.0"):
        Rubric.model_validate(bad)


def test_weight_out_of_range_rejected():
    bad = _valid_rubric_dict()
    bad["dimensions"]["accuracy"]["weight"] = 1.5
    with pytest.raises(ValidationError):
        Rubric.model_validate(bad)


def test_threshold_out_of_range_rejected():
    bad = _valid_rubric_dict()
    bad["threshold"] = 1.2
    with pytest.raises(ValidationError):
        Rubric.model_validate(bad)
