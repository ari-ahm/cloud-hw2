"""File queue, initially without synchronization for the race experiment."""

from pathlib import Path


def join(path: str | Path, name: str) -> int:
    if not isinstance(name, str) or "\n" in name or "\r" in name:
        raise ValueError("invalid name")
    name = name.strip()
    if not name or len(name) > 40:
        raise ValueError("invalid name")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    names = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    names.append(name)
    path.write_text("\n".join(names) + "\n", encoding="utf-8")
    return len(names)


def take(path: str | Path) -> str:
    path = Path(path)
    names = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    if not names:
        raise LookupError("empty")
    path.write_text("\n".join(names[1:]) + ("\n" if len(names) > 1 else ""), encoding="utf-8")
    return names[0]
