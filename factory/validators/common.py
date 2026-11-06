"""Shared helpers for factory validators."""
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "target", ".terraform"}


@dataclass(frozen=True)
class Finding:
    path: str
    message: str
    severity: str = "error"  # error | warning

    def __str__(self) -> str:
        return f"{self.severity.upper():7} {self.path}: {self.message}"


def iter_files(root: Path, suffixes: tuple[str, ...]):
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix in suffixes and not (set(p.relative_to(root).parts) & SKIP_DIRS):
            yield p


def rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix()
