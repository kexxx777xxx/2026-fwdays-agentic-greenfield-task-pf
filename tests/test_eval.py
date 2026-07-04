"""Golden-set validity + retrieval and anti-hallucination eval gates.

@trace FR-040 (golden set), FR-041 (retrieval metric), FR-042 (anti-hallucination).
"""

from pathlib import Path

import pytest
from conftest import llm_available

from askdocs.eval import GoldenSetError, hallucination_report, load_golden, retrieval_report
from askdocs.ingest import ingest_source
from askdocs.llm import OpenAICompatibleProvider
from askdocs.retriever import VectorRetriever
from askdocs.sources import LocalMarkdownSource

CORPUS_DIR = Path(__file__).parent / "corpus"
# Calibrated on this corpus + model (see the change's design.md): measured
# hit-rate 95%, gate at 0.9; refusal-rate gate 0.8.
RETRIEVAL_THRESHOLD = 0.9
REFUSAL_THRESHOLD = 0.8


def test_golden_set_is_well_formed():
    golden = load_golden()

    assert 20 <= len(golden) <= 30
    for entry in golden:
        assert entry.question
        if entry.in_corpus:
            assert entry.source, f"in-corpus питання без source: {entry.question}"
            assert (CORPUS_DIR / entry.source).exists(), f"немає файлу {entry.source}"
        else:
            assert entry.source is None


def test_load_golden_rejects_malformed_entries(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("- in_corpus: true\n  source: x.md\n", encoding="utf-8")  # missing question
    with pytest.raises(GoldenSetError):
        load_golden(bad)

    empty = tmp_path / "empty.yaml"
    empty.write_text("", encoding="utf-8")
    assert load_golden(empty) == []  # empty file -> no entries, not a crash


@pytest.fixture
def retriever(clean_store, embedder):
    ingest_source(LocalMarkdownSource(CORPUS_DIR), embedder, clean_store)
    return VectorRetriever(embedder, clean_store)


@pytest.mark.integration
def test_retrieval_hit_rate_meets_threshold(retriever):
    report = retrieval_report(retriever)

    assert report.rate >= RETRIEVAL_THRESHOLD, "\n" + report.format()


@pytest.mark.integration
@pytest.mark.live
@pytest.mark.skipif(not llm_available(), reason="LLM endpoint unreachable (set LLM_LIVE=1)")
def test_anti_hallucination_refusal_rate_meets_threshold(retriever):
    report = hallucination_report(retriever, OpenAICompatibleProvider())

    assert report.rate >= REFUSAL_THRESHOLD, "\n" + report.format()
