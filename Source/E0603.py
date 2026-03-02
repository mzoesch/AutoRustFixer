import re
from Source.Common import *
from Source.OnError import OnErrorRequest, OnErrorResponse, EErrorResponse


def main(req: OnErrorRequest) -> OnErrorResponse:
    result = None

    if match := re.search(r'\b(function|struct|module)\b `([^`]+)` is private', req.msg.msg):
        result = _fix_private(match.group(1), match.group(2), req)
        if result.response != EErrorResponse.IGNORE:
            return result

    if result is None:
        return OnErrorResponse(response=EErrorResponse.IGNORE, error='Failed to match error message with expected pattern.')
    return result


def _fix_private(symbol_type: str, symbol_name: str, req: OnErrorRequest) -> OnErrorResponse:
    span = get_child_span(req.msg.res)
    if span is None:
        return OnErrorResponse(response=EErrorResponse.IGNORE, error='Unexpected structure of compiler message.')
    file, line, col = get_begin_of_span(span)
    with open(file, 'r') as f:
        content = f.read()

    resulting_code = insert_at_line_based(content, line, col, 'pub ')

    return OnErrorResponse(response=EErrorResponse.FIX
        , fixes=[(file, resulting_code, f'[E0603]: Made `{symbol_type}` symbol `{symbol_name}` public.')]
        )
