"""Command-line interface.

Examples
--------
Offline demo (no API key needed):
    rubric-eval score --file data/samples.jsonl --mock

Real LLM-as-judge (needs an API key set):
    export OPENAI_API_KEY=...
    rubric-eval score --input "def add(a, b): return a + b"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rubric_eval.evaluator import evaluate
from rubric_eval.judge import LLMJudge
from rubric_eval.mock_judge import MockJudge
from rubric_eval.rubric import load_rubric


def _iter_inputs(args: argparse.Namespace):
    if args.input is not None:
        yield args.input
    if args.file is not None:
        for line in Path(args.file).read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            # accept either a raw line or a JSON object with an "output" field
            try:
                obj = json.loads(line)
                yield obj["output"] if isinstance(obj, dict) and "output" in obj else line
            except json.JSONDecodeError:
                yield line


def _run_score(args: argparse.Namespace) -> int:
    rubric = load_rubric(args.rubric)
    judge = MockJudge() if args.mock else LLMJudge(model=args.model, base_url=args.base_url)

    any_input = False
    for output in _iter_inputs(args):
        any_input = True
        decision = evaluate(output, rubric, judge)
        print(
            json.dumps(
                {
                    "ship": decision.ship,
                    "reason": decision.reason,
                    "aggregate": decision.aggregate,
                    "scores": {
                        k: round(v.score, 3)
                        for k, v in decision.result.dimension_scores.items()
                    },
                    "safety_pass": decision.result.safety_pass,
                    "output_preview": (output[:60] + "…") if len(output) > 60 else output,
                }
            )
        )

    if not any_input:
        print("no input: pass --input TEXT or --file PATH", file=sys.stderr)
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rubric-eval", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    score = sub.add_parser("score", help="score one or more outputs against the rubric")
    score.add_argument("--input", help="a single output string to score")
    score.add_argument("--file", help="a .jsonl or .txt file, one output per line")
    score.add_argument("--rubric", default="config/rubric.yaml", help="path to rubric YAML")
    score.add_argument("--mock", action="store_true", help="use the offline mock judge")
    score.add_argument("--model", default=None, help="judge model name (else LLM_MODEL)")
    score.add_argument("--base-url", default=None, help="OpenAI-compatible endpoint (else LLM_BASE_URL)")
    score.set_defaults(func=_run_score)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
