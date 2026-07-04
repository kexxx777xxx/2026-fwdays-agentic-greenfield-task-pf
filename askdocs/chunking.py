"""Structure-aware markdown chunking (FR-002).

Documents are split along markdown block boundaries, never by a blind character
count. A section (the blocks under a heading) is the default chunk; oversized
sections are split only between blocks, and an atomic block (table, fenced code,
list) larger than the budget stays whole. The heading trail is the chunk's
citation context.
"""

from dataclasses import dataclass

from markdown_it import MarkdownIt

CHUNK_SIZE_BUDGET = 1500  # soft target in characters; integrity wins over size

_OPEN_TYPES = {
    "paragraph_open",
    "table_open",
    "bullet_list_open",
    "ordered_list_open",
    "blockquote_open",
}
_LEAF_TYPES = {"fence", "code_block", "html_block", "hr"}


@dataclass(frozen=True)
class Chunk:
    source_path: str
    heading: str  # heading trail, e.g. "Двигун > Паливо"
    chunk_index: int
    text: str


def _parse_blocks(text: str) -> list[tuple[str, int | None, str]]:
    """Return top-level blocks as (kind, heading_level, block_text).

    Heading blocks are normalized to ATX form (`## Title`) with the title taken
    from the heading's `inline` child token, so setext (underline) headings and
    closed-ATX (`## Title ##`) headings never leak rule characters or trailing
    hashes into the trail or the chunk text.
    """
    lines = text.split("\n")
    tokens = MarkdownIt("commonmark").enable("table").parse(text)
    blocks: list[tuple[str, int | None, str]] = []
    for i, tok in enumerate(tokens):
        if tok.level != 0 or tok.map is None:
            continue
        start, end = tok.map
        if tok.type == "heading_open":
            level = int(tok.tag[1])
            nxt = tokens[i + 1] if i + 1 < len(tokens) else None
            title = nxt.content.strip() if nxt is not None and nxt.type == "inline" else ""
            blocks.append(("heading", level, f"{'#' * level} {title}".rstrip()))
        elif tok.type in _OPEN_TYPES or tok.type in _LEAF_TYPES:
            blocks.append(("block", None, "\n".join(lines[start:end]).rstrip()))
    return blocks


def _pack(block_texts: list[str], budget: int) -> list[str]:
    """Greedily join whole blocks up to the budget; never splits inside a block."""
    pieces: list[str] = []
    current: list[str] = []
    size = 0
    for block in block_texts:
        if current and size + len(block) > budget:
            pieces.append("\n\n".join(current))
            current, size = [], 0
        current.append(block)
        size += len(block)
    if current:
        pieces.append("\n\n".join(current))
    return [p for p in pieces if p.strip()]


def chunk_markdown(source_path: str, text: str, budget: int = CHUNK_SIZE_BUDGET) -> list[Chunk]:
    chunks: list[Chunk] = []
    trail: list[tuple[int, str]] = []  # (level, title)
    section: list[str] = []

    def flush() -> None:
        heading = " > ".join(title for _, title in trail)
        for piece in _pack(section, budget):
            chunks.append(Chunk(source_path, heading, len(chunks), piece))
        section.clear()

    for kind, level, block_text in _parse_blocks(text):
        if kind == "heading":
            flush()
            title = block_text.lstrip("#").strip()
            trail[:] = [t for t in trail if t[0] < level] + [(level, title)]
        section.append(block_text)
    flush()
    return chunks
