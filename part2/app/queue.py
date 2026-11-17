"""Queue operations serialized by a stable lock in the shared directory."""

import fcntl
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def _locked(path: Path):
    # Open a new descriptor per call, including calls in different threads.
    with path.with_suffix(".lock").open("a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def join(path: str | Path, name: str) -> int:
    if not isinstance(name, str) or "\n" in name or "\r" in name:
        raise ValueError("invalid name")
    name = name.strip()
    if not name or len(name) > 40:
        raise ValueError("invalid name")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _locked(path):
        names = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
        with path.open("a", encoding="utf-8") as queue:
            queue.write(name + "\n")
        return len(names) + 1


def take(path: str | Path) -> str:
    path = Path(path)
    if not path.parent.exists():
        raise LookupError("empty")
    with _locked(path):
        names = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
        if not names:
            raise LookupError("empty")
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent, prefix=".queue-", delete=False
            ) as queue:
                temporary = Path(queue.name)
                queue.writelines(name + "\n" for name in names[1:])
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return names[0]
