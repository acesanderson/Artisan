from pathlib import Path


def find_project_root(start_path: str | Path):
    """
    Find the root directory of the project by finding the closest pyproject.toml file.
    """
    start_path = Path(start_path).resolve()
    for parent in start_path.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise FileNotFoundError("No pyproject.toml found in parent directories.")
