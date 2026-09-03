"""The CLI runs end-to-end offline via --mock."""

import json

from rubric_eval.cli import main


def test_cli_scores_single_input(capsys):
    rc = main(["score", "--input", "def add(a, b): return a + b", "--mock"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    record = json.loads(out)
    assert "ship" in record and "aggregate" in record and "scores" in record


def test_cli_safety_gate_via_cli(capsys):
    rc = main(["score", "--input", "api_key = 'sk-live-secret'", "--mock"])
    record = json.loads(capsys.readouterr().out.strip())
    assert rc == 0
    assert record["safety_pass"] is False
    assert record["ship"] is False


def test_cli_no_input_errors(capsys):
    rc = main(["score", "--mock"])
    assert rc == 2
    assert "no input" in capsys.readouterr().err
