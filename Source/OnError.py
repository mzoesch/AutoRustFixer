from enum import Enum
from pathlib import Path
import Source.Compiler as compiler
from Source.Project import Project

class OnErrorRequest:
    def __init__(self
        , proj: Project
        , msg: compiler.CompilerMessage
        , res: compiler.Response
        ):
        self.proj = proj
        self.msg: compiler.CompilerMessage = msg
        self.res: compiler.Response = res


class EErrorResponse(Enum):
    IGNORE=0
    FIX=1


class OnErrorResponse:
    def __init__(self, *
        , response: EErrorResponse
        , error: str | None = None
        , fixes: list[tuple[Path, str, str|None]] | None = None
        ) -> None:
        self.response = response
        self.error = error
        self.fixes = fixes
