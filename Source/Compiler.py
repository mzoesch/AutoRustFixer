import os
import re
import json
import subprocess
from pathlib import Path
from enum import Enum
from Source.Globals import Globals


class Request:
    def __init__(self, *,
        compiler: str,
        file: Path,
        o: Path,
        crate_type: str | None = None
        ) -> None:
        self.compiler = compiler
        self.file = file
        self.o = o
        self.crate_type = crate_type


class ECompilerMessage(Enum):
    DIAGNOSTIC = 'diagnostic'


class CompilerMessage:
    discardable_msgs = [
        r'\d+ warning emitted',
        r'\d+ warnings emitted',
        r'aborting due to \d+ previous error',
        r'For more information about (this|an) error, try `rustc --explain E\d+`\.',
        r'Some errors have detailed explanations: (E\d+,\s*)+ E\d+\.',
        r'module `.*` should have a snake case name',
        ]

    def __init__(self, line: str) -> None:
        # If compiler produces invalid JSON, this will raise an exception. But that's ok.
        self.res = json.loads(line)
        if Globals.trace:
            print(json.dumps(self.res, indent=2))

        self.kind = ECompilerMessage(self.res.get('$message_type'))
        self.msg = self.res.get('message')
        self.error_code = CompilerMessage.find_error_code(self.res)
        if self.error_code is None:
            if CompilerMessage.is_discardable(self.msg):
                return
            if re.match(r'couldn\'t read `.*`: No such file or directory \(os error \d+\)', self.msg):
                raise ValueError(self.res.get('rendered', self.msg))
            if Globals.throw_on_unknown_compiler_message:
                print(repr(self))
                raise ValueError(f'Compiler error is not code related:\n\n{self}')
            return
        if CompilerMessage.is_discardable(self.msg):
            self.error_code = None
        return

    @staticmethod
    def find_error_code(res: dict) -> str | None:
        code = res.get('code')
        if code is None:
            return None
        if isinstance(code, dict):
            return CompilerMessage.find_error_code(res.get('code', {}))
        if isinstance(code, str):
            return code
        raise ValueError(f'Unexpected code format: {code}')

    @staticmethod
    def is_discardable(msg: str) -> bool:
        for regex in CompilerMessage.discardable_msgs:
            if re.match(regex, msg):
                return True
        return False

    def __repr__(self) -> str:
        return json.dumps(self.res, indent=4)

    def __str__(self) -> str:
        return self.res.get('rendered', '<unknown>')


class Response:
    def __init__(self) -> None:
        self.compiler_messages: list[CompilerMessage] = []


def compile(req: Request) -> Response:
    """
    :return: Code related error messages. Filters out diagnostic messages that are irrelevant for us.
    """
    res = Response()
    for line in _compile(req):
        msg = CompilerMessage(line)
        if msg.error_code is None: # discarded / verbose diagnostics
            continue
        res.compiler_messages.append(msg)
        continue
    return res


def _compile(req: Request) -> list[str]:
    cmd = [req.compiler, '--error-format=json', str(req.file), '-o', str(req.o), '-A', 'dead_code']
    if req.crate_type is not None:
        cmd.append(f'--crate-type={req.crate_type}')

    if Globals.verbose:
        print(f'Running command: {" ".join(cmd)}')

    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ) as p:
        stdout, stderr = p.communicate()
        lines = []
        if stdout:
            lines.extend(stdout.decode().splitlines())
        if stderr:
            lines.extend(stderr.decode().splitlines())
    return lines
