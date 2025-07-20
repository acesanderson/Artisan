from pathlib import Path

p = Path("project_context.xml")
project_context = p.read_text(encoding="utf-8") if p.exists() else ""
