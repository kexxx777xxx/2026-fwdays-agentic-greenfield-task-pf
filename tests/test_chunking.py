"""@trace FR-002 — chunking preserves structural block integrity.

Unit: pure markdown-it, no Qdrant / model.
"""

from askdocs.chunking import chunk_markdown

TABLE_DOC = """# Двигун

## Характеристики

| Параметр | Значення |
|---|---|
| Паливо | кавова гуща |
| Тяга | чотири ротори |
| Обсмаження | середнє |

Текст одразу після таблиці.
"""

CODE_DOC = """# API

Короткий опис.

```python
def ask(question):
    chunks = retrieve(question)
    return answer(chunks)
```

Кінець розділу.
"""

LIST_DOC = """# Кроки перед польотом

Виконай по порядку:

- Перевір рівень кавової гущі
- Прогрій ротори-турбінки
- Закрий кабіну
- Отримай дозвіл диспетчера

Готово до зльоту.
"""


def test_table_stays_in_one_chunk():
    chunks = chunk_markdown("d.md", TABLE_DOC)
    table_chunks = [c for c in chunks if "| Параметр |" in c.text]
    assert len(table_chunks) == 1
    c = table_chunks[0]
    assert "| Паливо | кавова гуща |" in c.text
    assert "| Обсмаження | середнє |" in c.text  # last row in the SAME chunk


def test_code_block_stays_in_one_chunk():
    chunks = chunk_markdown("a.md", CODE_DOC)
    code_chunks = [c for c in chunks if "def ask(question):" in c.text]
    assert len(code_chunks) == 1
    assert "return answer(chunks)" in code_chunks[0].text  # whole fence together


def test_list_stays_in_one_chunk():
    # The spec names lists as an atomic block group: all items in one chunk.
    chunks = chunk_markdown("l.md", LIST_DOC)
    list_chunks = [c for c in chunks if "Перевір рівень кавової гущі" in c.text]
    assert len(list_chunks) == 1
    assert "Отримай дозвіл диспетчера" in list_chunks[0].text  # last item, same chunk


def test_oversized_section_splits_on_block_boundaries():
    paras = "\n\n".join(f"Абзац номер {i} з деяким текстом про ГущоЛіт." for i in range(60))
    doc = f"# Розділ\n\n{paras}\n"
    chunks = chunk_markdown("big.md", doc, budget=200)
    assert len(chunks) > 1  # section was split
    # every paragraph survives AND is intact within exactly one chunk
    for i in range(60):
        hits = [c for c in chunks if f"Абзац номер {i} з деяким текстом про ГущоЛіт." in c.text]
        assert len(hits) == 1


def test_atomic_block_larger_than_budget_stays_whole():
    big_para = "Дуже довгий неподільний абзац. " * 40  # far over the budget
    doc = f"# H\n\n{big_para.strip()}\n"
    chunks = chunk_markdown("x.md", doc, budget=100)
    para_chunks = [c for c in chunks if "Дуже довгий неподільний абзац." in c.text]
    assert len(para_chunks) == 1  # not cut despite exceeding the budget


def test_heading_trail_is_the_citation_context():
    doc = "# Двигун\n\n## Паливо\n\nЗаправляти лише охолодженою гущею.\n"
    chunks = chunk_markdown("h.md", doc)
    body = [c for c in chunks if "охолодженою гущею" in c.text][0]
    assert body.heading == "Двигун > Паливо"


def test_setext_heading_does_not_leak_underline():
    # Underline (setext) headings must not put "======" into the trail or text.
    doc = "Двигун\n======\n\n## Паливо\n\nЗаправляти гущею.\n"
    chunks = chunk_markdown("s.md", doc)
    body = [c for c in chunks if "Заправляти гущею" in c.text][0]
    assert body.heading == "Двигун > Паливо"
    assert "======" not in "\n".join(c.text for c in chunks)


def test_closed_atx_heading_title_has_no_trailing_hashes():
    doc = "## Розділ ##\n\nтекст розділу.\n"
    chunks = chunk_markdown("c.md", doc)
    body = [c for c in chunks if "текст розділу" in c.text][0]
    assert body.heading == "Розділ"
