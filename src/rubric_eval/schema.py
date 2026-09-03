"""Validated data models for rubrics, judge results, and decisions.

Using Pydantic here is a deliberate design choice: a malformed rubric fails loudly
at load time (with a clear error) rather than silently producing wrong scores later.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class DimensionSpec(BaseModel):
    """One scored dimension of the rubric."""

    weight: float = Field(ge=0.0, le=1.0)
    definition: str


class SafetySpec(BaseModel):
    """The safety dimension. Modeled separately because it is a hard gate,
    not a weighted term (see Rubric / evaluator)."""

    mode: str = "hard_gate"
    definition: str


class Rubric(BaseModel):
    """A complete, validated rubric.

    Invariant enforced on load: the weighted dimensions' weights sum to 1.0.
    Safety is intentionally excluded from the weighted sum — it is a veto, not a term.
    """

    version: str
    threshold: float = Field(ge=0.0, le=1.0)
    dimensions: dict[str, DimensionSpec]
    safety: SafetySpec

    @field_validator("dimensions")
    @classmethod
    def _weights_sum_to_one(cls, v: dict[str, DimensionSpec]) -> dict[str, DimensionSpec]:
        total = sum(spec.weight for spec in v.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"weighted dimension weights must sum to 1.0, got {total:.4f}. "
                "(safety is a hard gate and is not part of this sum.)"
            )
        return v

    @property
    def weighted_dims(self) -> list[str]:
        return list(self.dimensions.keys())

    def weight(self, dim: str) -> float:
        return self.dimensions[dim].weight


class DimensionScore(BaseModel):
    """A judge's score for one dimension, with its reasoning."""

    score: float = Field(ge=0.0, le=1.0)
    rationale: str = ""


class JudgeResult(BaseModel):
    """The raw output of a judge: per-dimension scores plus a safety verdict."""

    dimension_scores: dict[str, DimensionScore]
    safety_pass: bool
    safety_rationale: str = ""


class Decision(BaseModel):
    """The final ship/rework decision for one output.

    `aggregate` is None when the safety gate fired, because the gate returns
    before any weighted aggregate is computed.
    """

    ship: bool
    aggregate: float | None
    reason: str
    result: JudgeResult
