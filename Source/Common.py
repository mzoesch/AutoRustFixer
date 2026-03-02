from pathlib import Path


def get_begin_of_span(span) -> tuple[Path, int, int]:
    file_name = span.get("file_name")
    line_start = span.get("line_start")
    col_start = span.get("column_start")
    assert (file_name is not None) and (line_start is not None) and (col_start is not None) \
        , 'Missing file_name, line_start, or column_start in span.'
    return Path(file_name), line_start, col_start


def insert_at_line_based(content: str, line: int, column: int, text: str) -> str:
    resulting_code = ''

    cur_line = 1
    cur_column = 1
    inserted = False
    skip_next = False
    for c in content:
        if skip_next:
            resulting_code += c
            skip_next = False
            continue
        if cur_line == line and cur_column == column:
            assert inserted == False
            resulting_code += text
            inserted = True
        resulting_code += c
        if c == '\\':
            skip_next = True
        if c == '\n':
            cur_line += 1
            cur_column = 1
        else:
            cur_column += 1
        continue
    assert inserted, 'Failed to insert pub keyword.'

    return resulting_code


def insert_at(content: str, where: int, text: str) -> str:
    resulting_code = content[:where] + text + content[where:]
    return resulting_code


def get_child(res) -> dict | None:
    children = res.get("children", {})
    if len(children) != 1:
        return None
    return children[0]


def get_span(child) -> dict | None:
    spans = child.get("spans", [])
    if len(spans) != 1:
        return None
    return spans[0]


def get_child_span(res) -> dict | None:
    child = get_child(res)
    if child is None:
        return None
    return get_span(child)


def apply_suggestion(span) -> str | None:
    suggestion = span.get("suggested_replacement", None)
    if suggestion is None:
        return None
    file_name, line_start, col_start = get_begin_of_span(span)
    with open(file_name, 'r') as f:
        content = f.read()
    resulting_code = insert_at_line_based(content, line_start, col_start, suggestion)
    return resulting_code
