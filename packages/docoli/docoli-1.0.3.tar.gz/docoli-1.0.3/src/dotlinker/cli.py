from __future__ import annotations

import argparse
from pathlib import Path

from .config import default_config_path, load_config, save_config, upsert_mapping
from .model import Mapping
from .backends.chezmoi import ChezmoiBackend
from .backends.cloud import CloudBackend
from .backends.base import RunContext


def main() -> None:
    p = argparse.ArgumentParser(prog="doli")

    p.add_argument(
        "-c",
        "--config",
        help="Path to config file. Default: ~/.config/dotlinker/config.yaml (XDG-aware).",
        default=None,
    )

    sub = p.add_subparsers(dest="cmd")  # NOT required -> we can show help on missing cmd

    sub.add_parser("pull", help="Import local config into chezmoi/cloud and link back")

    a = sub.add_parser("add", help="Add a new mapping to the config")
    a.add_argument("-N", "--name", help="Mapping name (unique)")
    a.add_argument("-b", "--backend", choices=["chezmoi", "cloud"], help="Backend to use")
    a.add_argument("-s", "--src", help="Source path (original location)")
    a.add_argument("-d", "--dest", help="Destination path (required for cloud backend)")
    a.add_argument("-r", "--replace", action="store_true", help="Replace existing mapping with same name")

    args = p.parse_args()

    # If no subcommand is provided: show help and exit successfully
    if args.cmd is None:
        p.print_help()
        return

    cfg = Path(args.config).expanduser().resolve() if args.config else default_config_path()

    if args.cmd == "add":
        if not args.name or not args.backend or not args.src:
            raise SystemExit("add requires: --name, --backend, --src (or -N/-b/-s).")

        m = Mapping(args.name, args.backend, args.src, args.dest)
        items = load_config(cfg)
        items = upsert_mapping(items, m, replace=bool(args.replace))
        save_config(cfg, items)
        return

    if args.cmd == "pull":
        ctx = RunContext()
        for m in load_config(cfg):
            if m.backend == "chezmoi":
                ChezmoiBackend().pull(m, ctx)
            elif m.backend == "cloud":
                CloudBackend().pull(m, ctx)
            else:
                raise SystemExit(f"Unknown backend: {m.backend}")
        return


if __name__ == "__main__":
    main()
