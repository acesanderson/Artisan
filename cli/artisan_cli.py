"""
CLI entry point for Artisan project.
"""

import argparse
from pathlib import Path
from Siphon.ingestion.github.flatten_directory import flatten_directory
from Artisan.main.find_project_root import find_project_root


def main():
    parser = argparse.ArgumentParser(
        description="Artisan CLI -- custom LLM commands for software dev."
    )
    # Add required argument for filepath
    parser.add_argument(
        "filepath",
        type=str,
        help="Path to the python file.",
    )
    parser.add_argument(
        "command",
        choices=["d", "docs", "t", "tests", "c", "consult"],
        default="d",
        nargs="?",
        help="Command to execute: generate, test, or deploy.",
    )
    args = parser.parse_args()
    # Validate filepath
    filepath = Path(args.filepath)
    assert filepath.exists(), f"File {filepath} does not exist."
    root = find_project_root(filepath)
    assert root.exists(), f"Project root {root} does not exist."
    print(f"Project root found at: {root}")
    context = flatten_directory(str(root))
    print("\n" + context)


if __name__ == "__main__":
    main()
