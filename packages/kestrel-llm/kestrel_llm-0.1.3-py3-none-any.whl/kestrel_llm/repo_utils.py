"""Helpers for resolving repo root and `LLM.txt` location.

The default behavior is optimized for CLI usage:
- If a user runs a command from a subdirectory, we search upward for `LLM.txt` / `llm.txt`.
- If nothing is found, we fall back to `$CONDOR_REPO_ROOT` (kept for compatibility) or CWD.
"""

from __future__ import annotations

import os

from pathlib import Path

DEFAULT_LLM_FILENAMES: tuple[str, ...] = ("LLM.txt", "llm.txt")
DEFAULT_REPO_ROOT_ENV_VAR = "CONDOR_REPO_ROOT"


def normalize_path(path: str) -> str:
    """Return a normalized absolute path for a filesystem path string."""
    return os.path.normpath(os.path.abspath(path))


def find_llm_file_upwards(
    start_dir: str | os.PathLike[str],
    *,
    filenames: tuple[str, ...] = DEFAULT_LLM_FILENAMES,
) -> str | None:
    """Search upward from start_dir for an LLM file and return its absolute path."""
    current = Path(start_dir).resolve()

    while True:
        for name in filenames:
            candidate = current / name
            if candidate.exists():
                return str(candidate)

        # Stop at filesystem root
        if current.parent == current:
            return None
        current = current.parent


def _pick_llm_file_for_repo_root(repo_root_abs: str) -> str:
    """Prefer an existing LLM file at the repo root; otherwise default to `LLM.txt`."""
    for name in DEFAULT_LLM_FILENAMES:
        candidate = os.path.join(repo_root_abs, name)
        if os.path.exists(candidate):
            return normalize_path(candidate)
    return normalize_path(os.path.join(repo_root_abs, "LLM.txt"))


def resolve_repo_root_and_llm_file(
    *,
    repo_root: str | None,
    llm_file: str | None,
    start_dir: str | None = None,
    repo_root_env_var: str = DEFAULT_REPO_ROOT_ENV_VAR,
) -> tuple[str, str]:
    """Resolve (repo_root_abs, llm_file_abs) from CLI inputs and environment."""
    if llm_file:
        llm_file_abs = normalize_path(llm_file)
        repo_root_abs = (
            normalize_path(repo_root)
            if repo_root
            else normalize_path(str(Path(llm_file_abs).parent))
        )
        return repo_root_abs, llm_file_abs

    if repo_root:
        repo_root_abs = normalize_path(repo_root)
        return repo_root_abs, _pick_llm_file_for_repo_root(repo_root_abs)

    start = start_dir or os.getcwd()
    found_llm = find_llm_file_upwards(start)
    if found_llm:
        llm_file_abs = normalize_path(found_llm)
        repo_root_abs = normalize_path(str(Path(llm_file_abs).parent))
        return repo_root_abs, llm_file_abs

    env_repo_root = os.environ.get(repo_root_env_var)
    if env_repo_root:
        repo_root_abs = normalize_path(env_repo_root)
    else:
        repo_root_abs = normalize_path(start)

    return repo_root_abs, _pick_llm_file_for_repo_root(repo_root_abs)
