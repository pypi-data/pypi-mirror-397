import subprocess
from ..util import expand
from .base import RunContext
from ..model import Mapping

class ChezmoiBackend:
    def __init__(self, exe="chezmoi"):
        self.exe = exe

    def pull(self, m: Mapping, ctx: RunContext):
        if ctx.dry_run:
            return
        subprocess.run([self.exe, "add", str(expand(m.src))], check=True)
