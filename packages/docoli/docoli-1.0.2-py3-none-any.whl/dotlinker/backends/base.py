from dataclasses import dataclass
from typing import Protocol
from ..model import Mapping

@dataclass(frozen=True)
class RunContext:
    dry_run: bool = False
    verbose: bool = False

class Backend(Protocol):
    def pull(self, m: Mapping, ctx: RunContext) -> None: ...
