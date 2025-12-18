from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from dotlinker.backends.cloud import CloudBackend
from dotlinker.backends.base import RunContext
from dotlinker.model import Mapping


class TestCloudBackend(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["DOTLINKER_TIMESTAMP"] = "20251216T170000"

    def tearDown(self) -> None:
        os.environ.pop("DOTLINKER_TIMESTAMP", None)

    def test_copies_file_then_links_and_backs_up_src(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            src = root / "home" / ".gitconfig"
            dest = root / "cloud" / ".gitconfig"
            src.parent.mkdir(parents=True, exist_ok=True)
            dest.parent.mkdir(parents=True, exist_ok=True)

            src.write_text("A", encoding="utf-8")

            m = Mapping(name="gitconfig", backend="cloud", src=str(src), dest=str(dest))
            CloudBackend().pull(m, RunContext(dry_run=False, verbose=False))

            self.assertTrue(dest.exists())
            self.assertEqual(dest.read_text(encoding="utf-8"), "A")

            self.assertTrue(src.is_symlink())
            self.assertEqual(src.resolve(), dest.resolve())

            bak = src.with_name(src.name + ".20251216T170000.bak")
            self.assertTrue(bak.exists())
            self.assertEqual(bak.read_text(encoding="utf-8"), "A")

    def test_backs_up_existing_dest_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            src = root / "home" / ".vimrc"
            dest = root / "cloud" / ".vimrc"
            src.parent.mkdir(parents=True, exist_ok=True)
            dest.parent.mkdir(parents=True, exist_ok=True)

            src.write_text("NEW", encoding="utf-8")
            dest.write_text("OLD", encoding="utf-8")

            m = Mapping(name="vimrc", backend="cloud", src=str(src), dest=str(dest))
            CloudBackend().pull(m, RunContext(dry_run=False, verbose=False))

            bak_dest = dest.with_name(dest.name + ".20251216T170000.bak")
            self.assertTrue(bak_dest.exists())
            self.assertEqual(bak_dest.read_text(encoding="utf-8"), "OLD")
            self.assertEqual(dest.read_text(encoding="utf-8"), "NEW")
            self.assertTrue(src.is_symlink())

    def test_noop_when_already_linked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            src = root / "home" / ".zshrc"
            dest = root / "cloud" / ".zshrc"
            src.parent.mkdir(parents=True, exist_ok=True)
            dest.parent.mkdir(parents=True, exist_ok=True)

            dest.write_text("X", encoding="utf-8")
            src.symlink_to(dest)

            m = Mapping(name="zshrc", backend="cloud", src=str(src), dest=str(dest))
            CloudBackend().pull(m, RunContext(dry_run=False, verbose=False))

            self.assertTrue(src.is_symlink())
            self.assertEqual(src.resolve(), dest.resolve())
            self.assertEqual(dest.read_text(encoding="utf-8"), "X")

    def test_requires_dest(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            src = root / "home" / ".x"
            src.parent.mkdir(parents=True, exist_ok=True)
            src.write_text("x", encoding="utf-8")

            m = Mapping(name="x", backend="cloud", src=str(src), dest=None)
            with self.assertRaises(ValueError):
                CloudBackend().pull(m, RunContext(dry_run=False, verbose=False))
