import re
from pathlib import Path


def get_begin_of_span(span) -> tuple[Path, int, int]:
    file_name = span.get('file_name')
    line_start = span.get('line_start')
    col_start = span.get('column_start')
    assert (file_name is not None) and (line_start is not None) and (col_start is not None) \
        , 'Missing file_name, line_start, or column_start in span.'
    return Path(file_name), line_start, col_start


def get_range_of_span(span) -> tuple[Path, int, int]:
    file_name = span.get('file_name')
    begin = span.get('byte_start')
    end = span.get('byte_end')
    assert (file_name is not None) and (begin is not None) and (end is not None) \
        , 'Missing file_name, byte_start, or byte_end in span.'
    return Path(file_name), begin, end


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
    assert inserted, 'Failed to insert text.'

    return resulting_code


def insert_at(content: str, where: int, text: str) -> str:
    resulting_code = content[:where] + text + content[where:]
    return resulting_code


def replace_bytes(content: str, begin: int, end: int, text: str) -> str:
    resulting_code = content[:begin] + text + content[end:]
    return resulting_code


def get_child(res) -> dict | None:
    children = res.get('children', {})
    if len(children) != 1:
        return None
    return children[0]


def get_child_where(res, where: str, field_label = 'message') -> dict | None:
    children = res.get('children', {})
    for child in children:
        field = child.get(field_label, None)
        if field is None:
            continue
        if re.match(where, field):
            return child
        continue
    return None


def get_span(child) -> dict | None:
    spans = child.get('spans', [])
    if len(spans) != 1:
        return None
    return spans[0]


def get_primary_span(child) -> dict | None:
    spans = child.get('spans', [])
    for span in spans:
        if span.get('is_primary', False):
            return span
    return None


def get_text_of_span(span) -> str | None:
    text = span.get('text', [])
    if len(text) != 1:
        return None
    return text[0].get('text', None)


def get_child_span(res) -> dict | None:
    child = get_child(res)
    if child is None:
        return None
    return get_span(child)


def apply_suggestion(span) -> str | None:
    suggestion = span.get('suggested_replacement', None)
    if suggestion is None:
        return None
    file_name, begin, end = get_range_of_span(span)
    with open(file_name, 'r') as f:
        content = f.read()
    resulting_code = replace_bytes(content, begin, end, suggestion)
    return resulting_code


def merge_str_with_overlap(a, b):
    max_overlap = 0
    for i in range(1, min(len(a), len(b)) + 1):
        if a[-i:] == b[:i]:
            max_overlap = i
        continue
    return a + b[max_overlap:]


def non_overlapping_prefix(a, b):
    for i in range(min(len(a), len(b)), 0, -1):
        if a.endswith(b[:i]):
            return a[:-i]
        continue
    return a
