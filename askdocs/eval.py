"""Eval: golden-set retrieval hit-rate and anti-hallucination refusal-rate.

    docker compose run --rm app python -m askdocs.eval

Retrieval eval needs only Qdrant + embeddings; the honesty eval needs the LLM.
Covers FR-040 (golden set), FR-041 (retrieval metric), FR-042 (anti-hallucination).
"""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

from askdocs.answer import answer_question
from askdocs.llm import LLMProvider
from askdocs.retriever import Retriever

GOLDEN_PATH = Path(__file__).parent.parent / "tests" / "golden.yaml"
DEFAULT_K = 5


@dataclass(frozen=True)
class GoldenEntry:
    question: str
    in_corpus: bool
    source: str | None


@dataclass(frozen=True)
class QuestionResult:
    question: str
    ok: bool
    detail: str


@dataclass(frozen=True)
class Report:
    title: str
    results: list[QuestionResult]

    @property
    def rate(self) -> float:
        return sum(r.ok for r in self.results) / len(self.results) if self.results else 0.0

    @property
    def misses(self) -> list[QuestionResult]:
        return [r for r in self.results if not r.ok]

    def format(self) -> str:
        passed = sum(r.ok for r in self.results)
        lines = [f"{self.title}: {self.rate:.0%} ({passed}/{len(self.results)})"]
        for r in self.misses:
            lines.append(f"  MISS: {r.question} — {r.detail}")
        return "\n".join(lines)


class GoldenSetError(ValueError):
    """Raised when the golden set file is malformed."""


def load_golden(path: Path = GOLDEN_PATH) -> list[GoldenEntry]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(raw, list):
        raise GoldenSetError(f"{path}: expected a list of entries, got {type(raw).__name__}")
    entries: list[GoldenEntry] = []
    for i, e in enumerate(raw):
        if not isinstance(e, dict) or "question" not in e or "in_corpus" not in e:
            raise GoldenSetError(f"{path}: entry #{i} must have 'question' and 'in_corpus'")
        entries.append(GoldenEntry(e["question"], e["in_corpus"], e.get("source")))
    return entries


def retrieval_report(retriever: Retriever, golden=None, k: int = DEFAULT_K) -> Report:
    golden = golden if golden is not None else load_golden()
    results = []
    for entry in golden:
        if not entry.in_corpus:
            continue
        sources = {c.source_path for c in retriever.retrieve(entry.question, k=k)}
        ok = entry.source in sources
        results.append(
            QuestionResult(
                entry.question, ok, f"очікували {entry.source}, отримали {sorted(sources)}"
            )
        )
    return Report(f"Retrieval hit-rate@{k}", results)


def hallucination_report(
    retriever: Retriever, llm: LLMProvider, golden=None, k: int = DEFAULT_K
) -> Report:
    golden = golden if golden is not None else load_golden()
    results = []
    for entry in golden:
        if entry.in_corpus:
            continue
        answer = answer_question(entry.question, retriever, llm, k=k)
        results.append(
            QuestionResult(
                entry.question,
                not answer.found,
                f"очікували відмову, отримали: {answer.text[:80]}",
            )
        )
    return Report("Anti-hallucination refusal-rate", results)


def main() -> int:
    from askdocs.embeddings import SentenceTransformersProvider
    from askdocs.ingest import ingest_source
    from askdocs.llm import OpenAICompatibleProvider
    from askdocs.retriever import VectorRetriever
    from askdocs.sources import LocalMarkdownSource
    from askdocs.store import QdrantStore

    # The golden set is written against the ГущоЛіт fixture corpus, so the eval
    # always measures against THAT — never the user's mounted /corpus — and uses
    # its own collection so it never pollutes the user's index.
    corpus = str(Path(__file__).parent.parent / "tests" / "corpus")
    embedder = SentenceTransformersProvider()
    store = QdrantStore(
        url=os.environ.get("QDRANT_URL", "http://localhost:6333"),
        collection="askdocs_eval",
        dimension=embedder.dimension,
    )
    ingest_source(LocalMarkdownSource(corpus), embedder, store)
    retriever = VectorRetriever(embedder, store)

    print(retrieval_report(retriever).format())
    print()
    print(hallucination_report(retriever, OpenAICompatibleProvider()).format())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
