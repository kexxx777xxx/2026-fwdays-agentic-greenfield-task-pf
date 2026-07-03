"""@trace FR-001 — DocSource loads local .md recursively, ignores the rest."""

from askdocs.sources import LocalMarkdownSource


def test_discovers_markdown_recursively(corpus_dir):
    docs = LocalMarkdownSource(corpus_dir).documents()
    paths = {d.source_path for d in docs}
    # nested file is found...
    assert "dvyhun/palyvo.md" in paths
    assert "proekt.md" in paths
    # ...and every discovered doc is a .md file
    assert paths and all(p.endswith(".md") for p in paths)


def test_ignores_non_markdown(corpus_dir):
    paths = {d.source_path for d in LocalMarkdownSource(corpus_dir).documents()}
    assert "notatky.txt" not in paths
    assert not any(p.endswith(".txt") for p in paths)


def test_empty_corpus(tmp_path):
    assert LocalMarkdownSource(tmp_path).documents() == []
