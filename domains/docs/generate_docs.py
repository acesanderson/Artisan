"""
Entry point for docs generation.
"""

from Chain.prompt.prompt_loader import PromptLoader
from Artisan.main.find_project_root import find_project_root
from Artisan.logs.logging_config import configure_logging
from Siphon.ingestion.github.flatten_directory import flatten_directory
from pathlib import Path
from typing import Literal
import logging

logger = configure_logging(
    level=logging.INFO,
    console=True,
)


# Constants
Scope = Literal["project", "module", "file", "class", "function"]
dir_path = Path(__file__).parent
prompt_dir = dir_path / "prompts"
prompt_loader = PromptLoader(base_dir=prompt_dir)
preferred_model = "claude"


def determine_scope(filepath: str | Path, line_number: int = 0) -> tuple[Scope, str]:
    """
    Determine the scope of the documentation based on the file path and line number.

    Args:
        filepath (str | Path): Path to the file.
        line_number (int): Line number in the file (default is 0).

    Returns:
        A tuple containing:
        Scope: The determined scope for documentation.
        str: The name of the element (if applicable).
    """
    logger.info(f"Determining scope for {filepath} at line {line_number}.")
    filepath = Path(filepath).resolve()
    assert filepath.exists(), f"File {filepath} does not exist."

    root = find_project_root(filepath)

    # filter with conditionals
    ## if filepath is a directory, we will be generating README (project scope)
    if filepath.is_dir():
        logger.info(f"File {filepath} is a directory, we will be generating README.")
        line_number = 0
        return "project", ""

    ## if filename contains "README.md" and is in root: "project"
    if filepath.name == "README.md" and filepath.parent == root:
        logger.info(f"File {filepath} is a README.md in the root, returning 'project'.")
        return "project", ""

    ## if filename contains "__init__.py": "module"
    if filepath.name == "__init__.py":
        logger.info(f"File {filepath} is an __init__.py file, returning 'module'.")
        return "module", ""

    ## if line_number < 2: "file"
    if line_number < 2:
        logger.info(f"Line number {line_number} is less than 2, returning 'file'.")
        return "file", ""

    ## if line_number > 4, introspect into script to determine if this is a class or a function
    ### retrieve text of the line number of the file
    script_text = filepath.read_text()
    lines = script_text.splitlines()
    if line_number < len(lines):
        line_text = lines[line_number - 1].strip()
    else:
        line_text = ""
    ### if line_text starts with "def ": "function"
    if line_text.startswith("def "):
        # Extract the function name from the line text
        function_name = line_text.split("(")[0][
            4:
        ].strip()  # Remove 'def ' and trailing spaces
        logger.info(
            f"Line {line_number} in {filepath} starts with 'def ', returning 'function'."
        )
        logger.info(f"Function name: {function_name}")
        return "function", function_name
    ### if line_text starts with "class ": "class"
    if line_text.startswith("class "):
        # Extract the class name from the line text
        class_name = line_text.split("(")[0][6:].strip()
        logger.info(
            f"Line {line_number} in {filepath} starts with 'class ', returning 'class'."
        )
        logger.info(f"Class name: {class_name}")
        return "class", class_name
    ### otherwise, raise ValueError
    logger.error(f"Could not determine scope for {filepath} at line {line_number}.")
    raise ValueError(
        f"Could not determine scope for {filepath} at line {line_number}. "
        "Please specify the scope explicitly."
    )


def generate_docs(
    filepath: str | Path,
    line_number: int = 0,
):
    """
    Generate documentation for the specified scope of the project.

    Args:
        filepath (str | Path): Path to the file or directory.
        line_number (int): Optional line number to start from (default is 0).
    """
    # Validate filepath
    filepath = Path(filepath).resolve()
    assert filepath.exists(), f"File or directory {filepath} does not exist."
    logger.info(f"Generating docs for {filepath} at line {line_number}.")

    # Determine the scope
    ## if filepath is a directory, we will be generating README (project scope)
    ## All other cases, we will determine the scope based on the file and line number
    scope, element_name = determine_scope(filepath, line_number)
    logger.info(f"Determined scope: {scope}")

    from Siphon.ingestion.github.flatten_directory import flatten_directory
    from Chain import Model, Chain

    # Get script text
    if filepath.is_dir():
        script_text = ""
    else:
        script_text = filepath.read_text()

    # Get project context
    project_context = flatten_directory(str(find_project_root(filepath)))

    # Get prompt from prompt loader
    prompt = prompt_loader[scope]
    logger.info(f"Using prompt: {scope}.jinja2")
    model = Model(preferred_model)
    chain = Chain(model=model, prompt=prompt)
    response = chain.run(
        input_variables={
            "script_text": script_text,
            "project_context": project_context,
            "element_name": element_name,
        }
    )
    print(response)


if __name__ == "__main__":
    file_path = Path("example.py")
    from Artisan.tests.fixtures.project_context import project_context

    project_context = project_context.strip()
    # 0 for file, 7 for function, 18 for class
    d = generate_docs(file_path, line_number=18)
