import re
from Source.Common import *
from Source.Project import *
from Source.OnError import OnErrorRequest, OnErrorResponse, EErrorResponse


def main(req: OnErrorRequest) -> OnErrorResponse:
    result = None

    if match := re.search(r'field `([^`]+)` of struct `([^`]+)` is private', req.msg.msg):
        result = _fix_private(match.group(2), match.group(1), req)
        if result.response != EErrorResponse.IGNORE:
            return result

    if match := re.search(r'fields `([^`]+)` and `([^`]+)` of struct `([^`]+)` are private', req.msg.msg):
        result = _fix_private(match.group(3), match.group(2), req)
        if result.response != EErrorResponse.IGNORE:
            return result

    if match := re.search(r'fields (`[^`]+`,\s*)+ `[^`]+` and `([^`]+)` of struct `([^`]+)` are private', req.msg.msg):
        result = _fix_private(match.group(3), match.group(2), req)
        if result.response != EErrorResponse.IGNORE:
            return result

    if result is None:
        return OnErrorResponse(response=EErrorResponse.IGNORE, error='Failed to match error message with expected pattern.')
    return result


def _fix_private(symbol_name: str, field_name: str,  req: OnErrorRequest) -> OnErrorResponse:
    candidates = req.proj.find_all(ENode.STRUCT, symbol_name)
    if len(candidates) == 0:
        return OnErrorResponse(response=EErrorResponse.IGNORE, error=f'No candidates found for struct `{symbol_name}`.')
    if len(candidates) > 1:
        return OnErrorResponse(response=EErrorResponse.IGNORE, error=f'Ambiguous candidates found for struct `{symbol_name}`. Candidates: {[f for f in candidates.keys()]}.')
    file, parents = candidates.items().__iter__().__next__()
    assert len(parents) > 0
    if len(parents) > 1:
        return OnErrorResponse(response=EErrorResponse.IGNORE, error=f'Ambiguous candidates found for struct `{symbol_name}`. Candidates: {parents}.')
    parent = parents[0]

    children = file.find_all_from_parent(ENode.FIELD, parent, field_name)
    if len(children) == 0:
        return OnErrorResponse(response=EErrorResponse.IGNORE, error=f'No candidates found for field `{field_name}` of struct `{symbol_name}`.')
    if len(children) > 1:
        return OnErrorResponse(response=EErrorResponse.IGNORE, error=f'Ambiguous candidates found for field `{field_name}` of struct `{symbol_name}`. Candidates: {children}.')
    child = children[0]

    with open(file.path, 'r') as f:
        content = f.read()

    resulting_code = insert_at(content, child.node_range[0], 'pub ')

    return OnErrorResponse(response=EErrorResponse.FIX
        , fixes=[(file.path, resulting_code, f'[E0451]: Made field `{field_name}` of struct `{symbol_name}` public.')]
        )
