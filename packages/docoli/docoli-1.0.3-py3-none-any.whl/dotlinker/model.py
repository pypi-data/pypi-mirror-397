from dataclasses import dataclass
from typing import Literal, Optional

BackendName = Literal["chezmoi", "cloud"]

@dataclass(frozen=True)
class Mapping:
    name: str
    backend: BackendName
    src: str
    dest: Optional[str] = None
