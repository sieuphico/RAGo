import ast
from pathlib import Path

APP = Path(__file__).resolve().parents[2] / "app"


def _imports(path: Path) -> list[str]:
    names: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def test_import_rules() -> None:
    offenders = [
        str(p.relative_to(APP))
        for folder in ("modules", "api", "worker")
        for p in (APP / folder).rglob("*.py")
        if any(n == "app.adapters" or n.startswith("app.adapters.") for n in _imports(p))
    ]
    assert offenders == []
