import re
from Source.Common import *
from Source.Compiler import CompilerMessage, Response
from Source.OnError import OnErrorRequest, OnErrorResponse, EErrorResponse


def main(req: OnErrorRequest) -> OnErrorResponse:
    result = None

    if match := re.search(r'cannot find function `([^`]+)` in this scope', req.msg.msg):
        result = _make_scoped(match.group(1), req)
        if result.response != EErrorResponse.IGNORE:
            return result

    if result is None:
        return OnErrorResponse(response=EErrorResponse.IGNORE, error='Failed to match error message with expected pattern.')
    return result


def _make_scoped(symbol, req: OnErrorRequest) -> OnErrorResponse:
    child = get_child(req.msg.res)
    if child is None:
        return OnErrorResponse(response=EErrorResponse.IGNORE, error='Unexpected error message format.')

    if match := re.search(r'function `([^`]+)` exists but is inaccessible', child.get('message', '')):
        span = get_span(req.msg.res)
        if span is None:
            return OnErrorResponse(response=EErrorResponse.IGNORE, error='Unexpected error message format.')

        file, line, col = get_begin_of_span(span)
        with open(file, 'r') as f:
            content = f.read()
        resulting_code = insert_at_line_based(content, line, col, f'{match.group(1)[:match.group(1).find(symbol)]}')
        return OnErrorResponse(response=EErrorResponse.FIX
            , fixes=[(file, resulting_code, f'[E0425]: Added new scope to symbol `{symbol}`.')]
            )

    return OnErrorResponse(response=EErrorResponse.IGNORE, error='Unexpected error message format.')
