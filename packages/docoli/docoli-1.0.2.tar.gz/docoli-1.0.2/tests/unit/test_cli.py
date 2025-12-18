from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from dotlinker.cli import main


class TestCli(unittest.TestCase):
    def _run(self, argv: list[str]) -> tuple[int, str]:
        buf = io.StringIO()
        with patch("sys.argv", ["doli"] + argv), redirect_stdout(buf):
            try:
                main()
                return 0, buf.getvalue()
            except SystemExit as e:
                return int(e.code or 0), buf.getvalue()

    def test_no_subcommand_prints_help(self) -> None:
        rc, out = self._run([])
        self.assertEqual(rc, 0)
        self.assertIn("usage:", out)
        self.assertIn("{pull,add}", out)

    def test_add_writes_config(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "config.yaml"

            rc, _ = self._run(
                ["-c", str(cfg), "add", "-N", "zshrc", "-b", "chezmoi", "-s", "~/.zshrc"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(cfg.exists())
            text = cfg.read_text(encoding="utf-8")
            self.assertIn("zshrc", text)
            self.assertIn("chezmoi", text)

    def test_pull_calls_backends(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "config.yaml"
            # Create config with two mappings
            cfg.write_text(
                "mappings:\n"
                "  - name: zshrc\n"
                "    backend: chezmoi\n"
                "    src: ~/.zshrc\n"
                "  - name: nvim\n"
                "    backend: cloud\n"
                "    src: ~/.config/nvim\n"
                "    dest: ~/Nextcloud/dotfiles/.config/nvim\n",
                encoding="utf-8",
            )

            with patch("dotlinker.cli.ChezmoiBackend.pull") as chez_pull, patch(
                "dotlinker.cli.CloudBackend.pull"
            ) as cloud_pull:
                rc, _ = self._run(["-c", str(cfg), "pull"])
                self.assertEqual(rc, 0)
                self.assertEqual(chez_pull.call_count, 1)
                self.assertEqual(cloud_pull.call_count, 1)
