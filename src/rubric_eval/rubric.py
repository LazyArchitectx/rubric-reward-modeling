"""Load and validate a rubric from YAML."""

from __future__ import annotations

from pathlib import Path

import yaml

from rubric_eval.schema import Rubric


def load_rubric(path: str | Path) -> Rubric:
    """Load a rubric YAML file and validate it.

    Raises pydantic.ValidationError with a clear message if the rubric is malformed
    (e.g. weights that do not sum to 1.0, or a score weight outside [0, 1]).
    """
    raw = yaml.safe_load(Path(path).read_text())
    return Rubric.model_validate(raw)
