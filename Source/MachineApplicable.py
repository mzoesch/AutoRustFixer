from Source.Common import *
from Source.Project import *
from Source.OnError import OnErrorRequest, OnErrorResponse, EErrorResponse


def main(req: OnErrorRequest) -> OnErrorResponse:
    if (result := _traverse(req.msg.res)) is not None:
        return OnErrorResponse(response=EErrorResponse.FIX
           , fixes=[
                (Path(result[1].get('file_name')),
                 apply_suggestion(result[1]),
                 f'[{req.msg.error_code}]: Applied at [{result[1].get('line_start', 0)}:{result[1].get('column_start', 0)}]: {result[0]}')
                ]
           )

    return OnErrorResponse(response=EErrorResponse.IGNORE)


def _traverse(node: dict) -> tuple[str, dict] | None:
    primary_span = get_primary_span(node)
    if primary_span is not None:
        suggestion_applicability = primary_span.get('suggestion_applicability', None)
        if suggestion_applicability is not None and suggestion_applicability == 'MachineApplicable':
            return node.get('message', ''), primary_span

    for child in node.get('children', []):
        if (_span := _traverse(child)) is not None:
            return _span

    return None
