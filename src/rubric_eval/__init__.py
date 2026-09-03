"""Rubric-governed LLM output evaluation.

Turns a subjective "is this a good model output?" into a measurable, governed
decision: an LLM-as-judge scores each output on the rubric's dimensions, a safety
hard-gate can veto regardless of scores, and a weighted aggregate is compared to a
threshold to decide ship vs. rework.
"""

from rubric_eval.evaluator import evaluate
from rubric_eval.rubric import load_rubric
from rubric_eval.schema import Decision, JudgeResult, Rubric

__all__ = ["Decision", "JudgeResult", "Rubric", "evaluate", "load_rubric"]
__version__ = "1.0.0"
