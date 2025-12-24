import argparse
from pathlib import Path
from sharktanklang.interpreter import (
    compile_source,
    run_file,
    repl,
    SharkSyntaxError,
)

def main():
    parser = argparse.ArgumentParser(
        description="SharkTankLang — Shark Tank India themed programming language"
    )

    parser.add_argument(
        "command",
        choices=["run", "repl", "transpile"],
        help="run <file> | repl | transpile <input> <output>",
    )

    parser.add_argument("file", nargs="?", help="Input .stl file")
    parser.add_argument("output", nargs="?", help="Output .py file")

    args = parser.parse_args()

    try:
        if args.command == "run":
            if not args.file:
                print("Error: please provide a .stl file")
                return
            run_file(args.file)

        elif args.command == "repl":
            repl()

        elif args.command == "transpile":
            if not args.file or not args.output:
                print("Usage: sharktanklang transpile input.stl output.py")
                return
            src = Path(args.file).read_text()
            py = compile_source(src)
            Path(args.output).write_text(py)
            print(f"Transpiled to {args.output}")

    except SharkSyntaxError as e:
        print(e)

if __name__ == "__main__":
    main()
