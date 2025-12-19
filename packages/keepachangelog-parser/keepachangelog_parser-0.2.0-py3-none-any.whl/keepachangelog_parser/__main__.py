import argparse
import json
from pathlib import Path

import pyparsing as pp

from keepachangelog_parser.parser import ChangeLogDocument


def main():
    parser = argparse.ArgumentParser("keepachangelog_parser")
    parser.add_argument("file", help="path to file to CHANGELOG.md to parse", type=Path)
    args = parser.parse_args()

    with open(args.file) as f:
        text = f.read()

    try:
        doc = ChangeLogDocument()("doc")
        result = doc.parse_string(text, parse_all=True)
        print(json.dumps(result.as_dict(), indent=2))
    except pp.ParseException as pe:
        print(f"Message: {pe.msg}")
        print(f"Line number: {pe.lineno}")
        print(f"Column number: {pe.col}")
        print(f"Character index: {pe.loc}")
        print(f"Failing line (between ^ on following linw):\n^{pe.line}^")
        print()


if __name__ == "__main__":
    main()
