from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dotlinker.backends.chezmoi import ChezmoiBackend
from dotlinker.backends.base import RunContext
from dotlinker.model import Mapping


class TestChezmoiBackend(unittest.TestCase):
    def test_runs_add(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "zshrc"
            src.write_text("x", encoding="utf-8")

            m = Mapping(name="zshrc", backend="chezmoi", src=str(src), dest=None)
            backend = ChezmoiBackend(exe="chezmoi")

            with patch("subprocess.run") as run:
                backend.pull(m, RunContext(dry_run=False, verbose=False))
                run.assert_called_once()
                args, kwargs = run.call_args
                self.assertEqual(args[0][0:2], ["chezmoi", "add"])
                self.assertIn(str(src.resolve()), args[0])
                self.assertTrue(kwargs["check"])

    def test_dry_run_does_not_execute(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "zshrc"
            src.write_text("x", encoding="utf-8")

            m = Mapping(name="zshrc", backend="chezmoi", src=str(src), dest=None)
            backend = ChezmoiBackend(exe="chezmoi")

            with patch("subprocess.run") as run:
                backend.pull(m, RunContext(dry_run=True, verbose=False))
                run.assert_not_called()
