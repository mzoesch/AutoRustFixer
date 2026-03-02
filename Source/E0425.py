from Source.Compiler import CompilerMessage, Response
from Source.OnError import OnErrorRequest, OnErrorResponse, EErrorResponse


def main(req: OnErrorRequest) -> OnErrorResponse:
    raise RuntimeError('Unimplemented')
