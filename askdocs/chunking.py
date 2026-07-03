"""Chunking: split a document into stored units with a heading trail.

Slice 1 (add-rag-skeleton) uses a DELIBERATELY NAIVE splitter: group blank-line
separated blocks up to a size budget, tracking the latest markdown heading so
each chunk carries a heading trail for citation. `add-ingest-quality` replaces
this with a structure-aware splitter that guarantees tables/code/lists stay
intact (FR-002); do not build that here.
"""

import re
from dataclasses import dataclass

CHUNK_BUDGET = 800  # characters (naive; tuned properly in add-ingest-quality)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


@dataclass(frozen=True)
class Chunk:
    source_path: str
    chunk_index: int
    heading: str
    text: str


def _blocks(text: str) -> list[str]:
    """Blank-line separated blocks, in order."""
    return [b.strip("\n") for b in re.split(r"\n\s*\n", text) if b.strip()]


def chunk_document(source_path: str, text: str, budget: int = CHUNK_BUDGET) -> list[Chunk]:
    chunks: list[Chunk] = []
    heading = ""
    buffer: list[str] = []
    index = 0

    def flush() -> None:
        nonlocal index, buffer
        if buffer:
            chunks.append(
                Chunk(
                    source_path=source_path,
                    chunk_index=index,
                    heading=heading,
                    text="\n\n".join(buffer),
                )
            )
            index += 1
            buffer = []

    for block in _blocks(text):
        first_line = block.splitlines()[0] if block.splitlines() else ""
        m = _HEADING_RE.match(first_line)
        if m:
            # a heading starts a new section: flush the previous one, retitle
            flush()
            heading = m.group(2).strip()
        current_len = sum(len(b) for b in buffer)
        if buffer and current_len + len(block) > budget:
            flush()
        buffer.append(block)
    flush()
    return chunks
