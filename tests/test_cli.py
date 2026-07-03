"""@trace FR-030 — CLI prints answer + sources, honest miss, usage on no arg.

Unit: the answer pipeline is stubbed (no Qdrant, no live model).
"""

from askdocs import cli
from askdocs.answer import REFUSAL_TEXT, Answer


def _patch_pipeline(monkeypatch, answer):
    monkeypatch.setattr(cli, "_build_pipeline", lambda: (lambda q: answer))


def test_question_prints_answer_and_sources(monkeypatch, capsys):
    _patch_pipeline(monkeypatch, Answer(text="Двигун на гущі [1].", sources=["proekt.md"], found=True))
    rc = cli.main(["З", "чого", "двигун?"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Двигун на гущі" in out
    assert "proekt.md" in out
    assert "Джерела" in out


def test_out_of_corpus_prints_honest_miss(monkeypatch, capsys):
    _patch_pipeline(monkeypatch, Answer(text=REFUSAL_TEXT, sources=[], found=False))
    rc = cli.main(["питання поза корпусом"])
    out = capsys.readouterr().out
    assert rc == 0
    assert REFUSAL_TEXT in out


def test_missing_argument_prints_usage_and_nonzero(capsys):
    # under pytest, stdin is not a TTY → no-arg path returns usage + non-zero
    rc = cli.main([])
    err = capsys.readouterr().err
    assert rc != 0
    assert "usage" in err.lower()
