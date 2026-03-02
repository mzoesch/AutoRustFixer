import sys
import json
import argparse
import Source.Compiler as compiler
from Source import error_fix_fns
from Source.Globals import Globals
from Source.OnError import OnErrorRequest, OnErrorResponse, EErrorResponse
from pathlib import Path
from Source.Project import Project


def fix_loop(args) -> None:
    report = {
        'fixes': [],
        'iterations': 0,
        'final_error_count': 0,
        }

    cur_error_count = 0

    iteration = 0
    while iteration < args.max:
        iteration += 1
        if Globals.verbose:
            print(f'Iteration [{iteration}].')

        files: list[Path] = []
        for file in Path(args.f).parent.rglob('*.rs'):
            files.append(file)
        proj: Project = Project(files)

        res = compiler.compile(compiler.Request(
            compiler=args.c, file=Path(args.f),
            o=Path(args.o),
            crate_type=args.crate_type
            ))
        cur_error_count = len(res.compiler_messages)
        if len(res.compiler_messages) == 0:
            break

        recompile = False
        for msg in res.compiler_messages:
            fn = error_fix_fns.get(msg.error_code, None)
            if fn is None:
                if Globals.throw_on_unknown_error:
                    raise ValueError(f'[{msg.error_code}]: No such handler. \n{msg.res.get('rendered', '<unknown>')}.')
                if Globals.verbose:
                    print(f'[{msg.error_code}]: No such handler. \n{msg.res.get('rendered', '<unknown>')}.')
                continue
            res_fn: OnErrorResponse = fn(OnErrorRequest(proj=proj, msg=msg, res=res))

            if res_fn.response == EErrorResponse.IGNORE:
                if Globals.verbose:
                    if res_fn.error is not None:
                        print(f'[{msg.error_code}]: Ignoring error. Reason [{res_fn.error}]: \n{msg.res.get('rendered', '<unknown>')}')
                    else:
                        print(f'[{msg.error_code}]: Ignoring error: \n{msg.res.get('rendered', '<unknown>')}')
                continue
            elif res_fn.response == EErrorResponse.FIX:
                assert res_fn.fixes is not None and len(res_fn.fixes) > 0
                for file, fix, human_readable_fix in res_fn.fixes:
                    with open(file, 'w') as f:
                        f.write(fix)
                    report['fixes'].append({
                        'file': str(file),
                        'fix': human_readable_fix,
                        })
                recompile = True
                break
            else:
                raise ValueError(f'Unknown response [{res_fn.response}].')

        if recompile:
            continue
        break

    if Globals.verbose:
        print('Final report:')
    report['iterations'] = iteration
    report['final_error_count'] = cur_error_count
    if not Globals.quiet:
        print(json.dumps(report, indent=2))

    return None


def main(sys_args) -> None:
    parser = argparse.ArgumentParser(description='Automation tool.')
    parser.add_argument('-c', type=str, default='rustc', help='Compiler to use. Defaults to [rustc].')
    parser.add_argument('-f', type=str, required=True, help='File to compile.')
    parser.add_argument('-o', type=str, default='Temp/void', help='Output file. Defaults to [Temp/void].')
    parser.add_argument('-crate-type', type=str, required=False, help='Crate type.')
    parser.add_argument('-max', type=int, default=64, help='Maximum iterations. Defaults to [64].')
    parser.add_argument('-q', action='store_true', help='Quiet mode.')
    parser.add_argument('-v', action='store_true', help='Whether to emit verbose output.')
    parser.add_argument('-t', action='store_true', help='Whether to emit trace output.')
    parser.add_argument('-dev', action='store_true', help='Whether to enable development mode. This will cause the tool to throw errors if it encounters unknown scenarios.')
    args, _ = parser.parse_known_args(args=sys_args)

    if args.q:
        Globals.quiet = True
    if not Globals.quiet:
        if args.v:
            Globals.verbose = True
        if args.t:
            Globals.verbose = True
            Globals.trace = True
    if args.dev:
        Globals.throw_on_unknown_error = True
        Globals.throw_on_unknown_analysis = True
        Globals.throw_on_unknown_compiler_message = True

    fix_loop(args)

    return None


if __name__ == '__main__':
    main(sys.argv[1:])
