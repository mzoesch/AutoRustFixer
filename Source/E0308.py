from Source.Common import *
from Source.Project import *
from Source.OnError import OnErrorRequest, OnErrorResponse, EErrorResponse


def main(req: OnErrorRequest) -> OnErrorResponse:
    result = None

    if (child := get_child_where(req.msg.res, 'consider borrowing here')) is not None:
        span = get_span(child)
        if span is not None:
            return OnErrorResponse(response=EErrorResponse.FIX
            , fixes=[(Path(span.get('file_name')), apply_suggestion(span), '[E0308]: Applied suggested fix to borrow value.')]
            )

    if result is None:
        return OnErrorResponse(response=EErrorResponse.IGNORE, error='Failed to match error message with expected pattern.')
    return result
