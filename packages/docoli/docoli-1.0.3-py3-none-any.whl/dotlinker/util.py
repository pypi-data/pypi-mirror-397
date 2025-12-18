from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path


def expand(path: str) -> Path:
    """
    Expand user (~) and return an absolute path WITHOUT resolving symlinks.

    This is critical because resolving would destroy symlink information,
    which we need to detect "already linked" cases safely.
    """
    p = Path(os.path.expanduser(path))

    if not p.is_absolute():
        p = Path.cwd() / p

    # .absolute() does NOT resolve symlinks (unlike .resolve()).
    return p.absolute()


def timestamp() -> str:
    fixed = os.environ.get("DOTLINKER_TIMESTAMP")
    if fixed:
        return fixed
    return datetime.now().strftime("%Y%m%dT%H%M%S")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def is_same_symlink(src: Path, dest: Path) -> bool:
    """
    Return True if src is a symlink pointing to dest.

    Works even if dest doesn't exist (no resolve()).
    """
    if not src.is_symlink():
        return False

    try:
        link_target = Path(os.readlink(src))
    except OSError:
        return False

    # Handle relative symlink targets
    if not link_target.is_absolute():
        link_target = src.parent / link_target

    # Compare as absolute paths without following symlinks
    return link_target.absolute() == dest.absolute()
