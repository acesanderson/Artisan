"""
CLI entry point for Artisan project.
"""

import argparse, logging
from pathlib import Path
from Artisan.domains.docs.generate_docs import generate_docs
from Artisan.logs.logging_config import configure_logging

logger = configure_logging(
    level=logging.INFO,
    console=True,
)


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
    # Add optional argument for line number
    parser.add_argument(
        "--line",
        type=int,
        nargs="?",
        default=0,
        help="Line number to start from (default: 0).",
    )
    # parser.add_argument(
    #     "command",
    #     choices=["d", "docs", "t", "tests", "c", "consult"],
    #     default="d",
    #     nargs="?",
    #     help="Command to execute: generate, test, or deploy.",
    # )
    args = parser.parse_args()
    # Validate filepath
    filepath = Path(args.filepath)
    assert filepath.exists(), f"File {filepath} does not exist."
    # Run generate_docs
    logger.info(f"Generating docs for {filepath} at line {args.line}.")
    docs = generate_docs(filepath, line_number=args.line)
    print(docs)


if __name__ == "__main__":
    main()
