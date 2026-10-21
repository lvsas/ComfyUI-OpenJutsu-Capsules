"""Load the pack as a synthetic package so relative imports work in tests.

ComfyUI loads this directory as a package; the repository directory name contains
hyphens, which is not a valid Python identifier. Tests therefore register the pack
under a stable synthetic package name instead of relying on the folder name.
"""
import importlib
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "openjutsu_capsules"


def load(name):
    if PACKAGE not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            PACKAGE, ROOT / "__init__.py", submodule_search_locations=[str(ROOT)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[PACKAGE] = module
        spec.loader.exec_module(module)
    return importlib.import_module(f"{PACKAGE}.{name}")
