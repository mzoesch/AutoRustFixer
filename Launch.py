import sys
import json
import argparse
import Source.Compiler as compiler
import Source.MachineApplicable as machine_applicable
import Source.MaybeIncorrect as maybe_incorrect
from Source import error_fix_fns
from Source.Globals import Globals
from Source.OnError import OnErrorRequest, OnErrorResponse, EErrorResponse
from pathlib import Path
from Source.Project import Project


re_maybe_incorrect = [
    'consider importing this (function|module)',
    ]


def fix_loop(args) -> None:
    report = {
        'fixes': [],
        'iterations': 0,
        'final_error_count': 0,
        }

    def __apply(__res: OnErrorResponse) -> None:
        assert __res.fixes is not None and len(__res.fixes) > 0
        for __file, __fix, __human_readable_fix in __res.fixes:
            assert (__file is not None) and (__fix is not None)
            with open(__file, 'w') as f:
                f.write(__fix)
            report['fixes'].append({
                'file': str(file),
                'fix': __human_readable_fix,
                })
        return None

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
            if (res_suggestions := machine_applicable.main(OnErrorRequest(proj=proj, msg=msg, res=res))).response == EErrorResponse.FIX:
                __apply(res_suggestions)
                recompile = True
                break
            if Globals.only_machine_applicable:
                continue
            if Globals.maybes:
                if (res_suggestions := maybe_incorrect.main(OnErrorRequest(proj=proj, msg=msg, res=res), re_maybe_incorrect)).response == EErrorResponse.FIX:
                    __apply(res_suggestions)
                    recompile = True
                    break

            fn = error_fix_fns.get(msg.error_code, None)
            if fn is None:
                if Globals.throw_on_unknown_error:
                    raise ValueError(f'[{msg.error_code}]: No such handler. \n{msg.res.get('rendered', '<unknown>')}.')
                if Globals.verbose:
                    print(f'[{msg.error_code}]: No such handler. \n{msg.res.get('rendered', '<unknown>')}.')
                continue
            res_fn: OnErrorResponse = fn(OnErrorRequest(proj=proj, msg=msg, res=res))

            if res_fn.response == EErrorResponse.IGNORE:
                if Globals.throw_on_unknown_error:
                    raise ValueError(f'[{msg.error_code}]: Unhandled error. Reason [{res_fn.error}]: \n{msg.res.get('rendered', '<unknown>')}.')
                if Globals.verbose:
                    if res_fn.error is not None:
                        print(f'[{msg.error_code}]: Ignoring error. Reason [{res_fn.error}]: \n{msg.res.get('rendered', '<unknown>')}')
                    else:
                        print(f'[{msg.error_code}]: Ignoring error: \n{msg.res.get('rendered', '<unknown>')}')
                continue

            elif res_fn.response == EErrorResponse.FIX:
                __apply(res_fn)
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
        if Globals.pretty_print:
            print(json.dumps(report, indent=2))
        else:
            print(json.dumps(report, indent=None))

    return None


def main(sys_args) -> None:
    parser = argparse.ArgumentParser(description='Automation tool.')
    parser.add_argument('-c', type=str, default='rustc', help='Compiler to use. Defaults to [rustc].')
    parser.add_argument('-f', type=str, required=True, help='File to compile.')
    parser.add_argument('-o', type=str, default='Temp/void', help='Output file. Defaults to [Temp/void].')
    parser.add_argument('-crate-type', type=str, required=False, help='Crate type.')
    parser.add_argument('-max', type=int, default=64, help='Maximum iterations. Defaults to [64].')
    parser.add_argument('-only-machine-applicable', action='store_true', help='Whether to ignore messages that may be incorrect.')
    parser.add_argument('-no-maybes', action='store_true', help='Whether to ignore messages that may be incorrect.')
    parser.add_argument('-q', action='store_true', help='Quiet mode.')
    parser.add_argument('-v', action='store_true', help='Whether to emit verbose output.')
    parser.add_argument('-t', action='store_true', help='Whether to emit trace output.')
    parser.add_argument('-dev', action='store_true', help='Whether to enable development mode. This will cause the tool to throw errors if it encounters unknown scenarios.')
    args, _ = parser.parse_known_args(args=sys_args)

    if args.only_machine_applicable:
        Globals.only_machine_applicable = True
    if args.no_maybes:
        Globals.maybes = False
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
        Globals.pretty_print = True

    fix_loop(args)

    return None


if __name__ == '__main__':
    main(sys.argv[1:])
