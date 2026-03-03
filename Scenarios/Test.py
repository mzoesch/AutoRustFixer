import os
import subprocess
import json
from pathlib import Path


g_scenarios = [
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Correct'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Scope1'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Scope2'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Scope3'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Scope4'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Scope5'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Scope6'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Scope7'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Scope8'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Scope9'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/TypeMismatch1'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Visibility1'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Visibility2'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Visibility3'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Visibility4'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Visibility5'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Visibility6'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Visibility7'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Visibility8'],
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/VisibilityCombined'],

    # Most complex, therefore, most likely to fail, so we run it last.
    ['--f', 'client.rs', '--copy-dir', 'Scenarios/Combined1'],
    ]


def main(scenarios) -> None:
    errors: list[str] = []

    cwd = os.getcwd()
    try:
        os.chdir(Path(__file__).parent.parent)
        for idx, scenario in enumerate(scenarios):
            cmd = ['python3', './LaunchCopy.py'] + scenario

            print(f'[{idx + 1:0{len(str(len(scenarios)))}}/{len(scenarios)}] Running: {cmd[-1]} ...', end=' ', flush=True)
            with subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            ) as p:
                stdout, stderr = p.communicate()
                out = ''
                if stdout:
                    out += stdout.decode()
                if stderr:
                    out += stderr.decode()

            try:
                serialized = json.loads(out)
                if err_count := serialized.get('final_error_count', 1) != 0:
                    print(f'FAILED with {err_count} errors.')
                    errors.append(f'[{idx + 1}/{len(scenarios)}] Scenario failed with non-zero error count. Output was:\n{out}')
                else:
                    print(f'PASSED with {serialized.get('iterations', 0)} iterations.')
            except json.JSONDecodeError as e:
                print('FAILED to parse JSON output.')
                errors.append(f'[{idx + 1}/{len(scenarios)}] Failed to parse JSON output: {e}\nOutput was:\n{out}')
            continue

    finally:
        os.chdir(cwd)

    for error in errors:
        print(f'ERROR: {error}')
    print(f'Passed [{len(scenarios) - len(errors):0{len(str(len(scenarios)))}}/{len(scenarios)}].')

    return


if __name__ == '__main__':
    main(scenarios=g_scenarios)
