from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from dotlinker.config import default_config_path, load_config, save_config, upsert_mapping
from dotlinker.model import Mapping


class TestConfig(unittest.TestCase):
    def test_default_config_path_respects_xdg(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            xdg = Path(td) / "xdg"
            os.environ["XDG_CONFIG_HOME"] = str(xdg)

            p = default_config_path()
            self.assertEqual(p, xdg / "dotlinker" / "config.yaml")

    def test_load_config_missing_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "missing.yaml"
            self.assertEqual(load_config(cfg), [])

    def test_save_and_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "cfg.yaml"
            mappings = [
                Mapping(name="zshrc", backend="chezmoi", src="~/.zshrc", dest=None),
                Mapping(
                    name="nvim",
                    backend="cloud",
                    src="~/.config/nvim",
                    dest="~/Nextcloud/dotfiles/.config/nvim",
                ),
            ]

            save_config(cfg, mappings)
            loaded = load_config(cfg)
            self.assertEqual(loaded, mappings)

    def test_upsert_adds_when_missing(self) -> None:
        out = upsert_mapping([], Mapping("a", "chezmoi", "~/.a", None), replace=False)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].name, "a")

    def test_upsert_rejects_duplicate_without_replace(self) -> None:
        items = [Mapping("a", "chezmoi", "~/.a", None)]
        with self.assertRaises(ValueError):
            upsert_mapping(items, Mapping("a", "cloud", "~/.a", "~/x"), replace=False)

    def test_upsert_replaces_with_replace(self) -> None:
        items = [Mapping("a", "chezmoi", "~/.a", None)]
        out = upsert_mapping(items, Mapping("a", "cloud", "~/.a", "~/x"), replace=True)
        self.assertEqual(out[0].backend, "cloud")
        self.assertEqual(out[0].dest, "~/x")
