import re
from Source.Common import *
from Source.Project import *
from Source.OnError import OnErrorRequest, OnErrorResponse, EErrorResponse


def main(req: OnErrorRequest) -> OnErrorResponse:
    result = None

    if match := re.search(r'failed to resolve: use of unresolved module or unlinked crate `([^`]+)`', req.msg.msg):
        result = _fix_unresolved(match.group(1), req)
        if result.response != EErrorResponse.IGNORE:
            return result

    if result is None:
        return OnErrorResponse(response=EErrorResponse.IGNORE, error='Failed to match error message with expected pattern.')
    return result


def _fix_unresolved(crate: str, req: OnErrorRequest) -> OnErrorResponse:
    child = get_child(req.msg.res)
    if child is None:
        return OnErrorResponse(response=EErrorResponse.IGNORE, error='Unexpected structure of compiler message.')
    if child.get('level', '') != 'help':
        return OnErrorResponse(response=EErrorResponse.IGNORE, error='Child is not a suggested fix.')

    if re.match(r'to make use of source file .*, use `.*` in this file to declare the module', child.get('message', '')):
        span = get_span(child)
        result = apply_suggestion(span)
        if result is None:
            return OnErrorResponse(response=EErrorResponse.IGNORE, error='Failed to apply suggested fix.')
        return OnErrorResponse(response=EErrorResponse.FIX
            , fixes=[(span['file_name'], result, f'[E0433]: Added `{span['suggested_replacement']}`.')]
            )

    return OnErrorResponse(response=EErrorResponse.IGNORE, error='Failed to match the compiler error with expected pattern.')
