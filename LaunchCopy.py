import argparse
import sys
import shutil
import Launch


def main(sys_args) -> None:
    """
    Debug entry point for copying the targeted source files to a separate folder to make changes on these instead
    of the original files.
    This will result in the original files being left unchanged.
    """

    parser = argparse.ArgumentParser(description='Automation tool.')
    parser.add_argument('--f', type=str, required=True, help='File to compile. Will be prefixed with the copy directory.')
    parser.add_argument('--copy-dir', type=str, required=True, help='Directory to copy.')
    parser.add_argument('--clear-copy-dir', action='store_true', help='Clear the copy directory before copying.')
    parser.add_argument('--copy-dst', type=str, default=None, help='Destination directory for copying. Defaults to [None]. If None, then: Temp/[copy-dir].')
    args, _ = parser.parse_known_args(args=sys_args)

    if args.copy_dst is None:
        args.copy_dst = f'Temp/{args.copy_dir}'

    if args.clear_copy_dir:
        shutil.rmtree(args.copy_dst, ignore_errors=True)
    shutil.copytree(args.copy_dir, args.copy_dst, dirs_exist_ok=True, copy_function=shutil.copy2)

    main_args = sys_args
    main_args += ['-f', f'{args.copy_dst}/{args.f}']

    Launch.main(sys_args=main_args)
    return None


if __name__ == '__main__':
    main(sys.argv[1:])
