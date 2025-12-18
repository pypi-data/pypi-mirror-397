from __future__ import annotations

import shutil
from pathlib import Path

from ..model import Mapping
from ..util import ensure_parent, expand, is_same_symlink, timestamp
from .base import RunContext


class CloudBackend:
    def pull(self, m: Mapping, ctx: RunContext) -> None:
        if not m.dest:
            raise ValueError("cloud requires dest")

        src = expand(m.src)
        dest = expand(m.dest)

        # Safety: refuse destructive self-mapping
        if src.absolute() == dest.absolute():
            raise ValueError(f"cloud mapping '{m.name}' has src == dest, refusing: {src}")

        # Already linked correctly -> noop
        if is_same_symlink(src, dest):
            if ctx.verbose:
                print(f"[cloud] {m.name}: already linked")
            return

        # If src is a symlink, but not the correct one -> backup and replace
        if src.is_symlink():
            bak = src.with_name(src.name + "." + timestamp() + ".bak")
            if ctx.verbose or ctx.dry_run:
                print(f"[cloud] backup wrong symlink: {src} -> {bak}")
            if not ctx.dry_run:
                src.rename(bak)

        # Ensure destination parent exists
        ensure_parent(dest)

        # If src doesn't exist (fresh system), create dest skeleton and link back
        if not src.exists():
            if ctx.verbose:
                print(f"[cloud] {m.name}: src missing, creating dest skeleton and linking")
            if ctx.dry_run:
                return

            if not dest.exists():
                # MVP behavior: create empty file by default
                dest.touch(exist_ok=True)

            self._link(src, dest)
            return

        # If destination already exists -> backup it
        if dest.exists():
            dest_bak = dest.with_name(dest.name + "." + timestamp() + ".bak")
            if ctx.verbose or ctx.dry_run:
                print(f"[cloud] backup dest: {dest} -> {dest_bak}")
            if not ctx.dry_run:
                dest.rename(dest_bak)

        # Copy src -> dest
        if ctx.verbose or ctx.dry_run:
            print(f"[cloud] copy: {src} -> {dest}")

        if not ctx.dry_run:
            if src.is_dir():
                # copytree requires dest not exist
                shutil.copytree(src, dest, symlinks=True)
            else:
                shutil.copy2(src, dest)

        # Backup original src and replace with symlink
        src_bak = src.with_name(src.name + "." + timestamp() + ".bak")
        if ctx.verbose or ctx.dry_run:
            print(f"[cloud] backup src: {src} -> {src_bak}")

        if ctx.dry_run:
            return

        src.rename(src_bak)
        self._link(src, dest)

    def _link(self, src: Path, dest: Path) -> None:
        ensure_parent(src)
        # Use absolute target for MVP (simple + robust)
        src.symlink_to(dest)
