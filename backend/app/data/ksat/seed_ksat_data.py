"""Registry of KSAT exam seed modules.

Each registered exam lives in its own directory and exposes a seed.py
module with two attributes:

    EXAM_META: dict   # university, year, track, exam_type
    QUESTIONS: list[dict]  # per-question metadata + file paths

QUESTION dicts reference passage/prompt/example_answer as Paths under
the same exam directory. The loader in core/db.py reads those files at
seed time.

Directory names start with a year digit, so we load each seed.py by
absolute file path instead of `importlib.import_module`.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

_BASE = Path(__file__).parent


def _load_seed(path: Path) -> ModuleType:
    """Load a seed.py as a module from an absolute file path."""
    if not path.is_file():
        raise FileNotFoundError(f"Seed module not found: {path}")
    slug = f"{path.parent.parent.name}__{path.parent.name}"
    spec = importlib.util.spec_from_file_location(f"ksat_seed__{slug}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SEED_EXAMS: list[ModuleType] = [
    _load_seed(_BASE / "2025_cau_mock_essay" / "humanities" / "seed.py"),
    _load_seed(_BASE / "2026_inha_official_essay" / "humanities" / "seed.py"),
]
