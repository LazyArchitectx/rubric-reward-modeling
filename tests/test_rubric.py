"""The shipped rubric loads and is internally consistent."""

from rubric_eval.rubric import load_rubric


def test_project_rubric_loads():
    rubric = load_rubric("config/rubric.yaml")
    assert rubric.threshold == 0.80
    assert set(rubric.weighted_dims) == {"accuracy", "logic", "formatting", "efficiency"}


def test_project_rubric_weights_sum_to_one():
    rubric = load_rubric("config/rubric.yaml")
    total = sum(rubric.weight(d) for d in rubric.weighted_dims)
    assert abs(total - 1.0) < 1e-6
