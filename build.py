from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

from wingline.package import build, verify_pack


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "dist"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Wingline Windows cursor packs.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the existing cursor files and ZIP archives without rebuilding",
    )
    args = parser.parse_args(argv)
    try:
        if args.check:
            verify_pack(OUTPUT_DIR)
            print("Wingline cursor packs verified.")
        else:
            build(OUTPUT_DIR)
            print("Built and verified Wingline White, Wingline Black, and combined ZIP packs.")
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"Build check failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
