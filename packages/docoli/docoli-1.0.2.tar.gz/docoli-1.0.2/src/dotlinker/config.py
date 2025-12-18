import os
from pathlib import Path
from dataclasses import asdict
import yaml
from .model import Mapping

def default_config_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    return Path(xdg) / "dotlinker" / "config.yaml"

def load_config(path: Path):
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text()) or {}
    return [Mapping(**m) for m in data.get("mappings", [])]

def save_config(path: Path, mappings):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"mappings": [asdict(m) for m in mappings]}, sort_keys=False))

def upsert_mapping(mappings, new, replace=False):
    for i, m in enumerate(mappings):
        if m.name == new.name:
            if not replace:
                raise ValueError("Mapping already exists")
            mappings[i] = new
            return mappings
    return mappings + [new]
