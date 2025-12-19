from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Iterator, Optional


_MISSING_LINE_RE = re.compile(
    r"^(?P<mod>[^:]+): Failed to find (?P<name>.+?) hash! Old:\s*(?P<hash>.+?)\s*$"
)


@dataclass(frozen=True)
class MissingHash:
    mod: str
    name: str
    old_hash: int
    old_hash_raw: str


def _parse_hash_token(token: str) -> int:
    token = token.strip()
    lower = token.lower()
    if lower.endswith("ul"):
        token = token[:-2]
    elif lower.endswith("u"):
        token = token[:-1]
    return int(token, 0)


def parse_missing_log_lines(lines: Iterable[str]) -> Iterator[MissingHash]:
    for line in lines:
        line = line.rstrip("\n")
        m = _MISSING_LINE_RE.match(line.strip())
        if not m:
            continue
        raw = m.group("hash").strip()
        yield MissingHash(
            mod=m.group("mod").strip(),
            name=m.group("name").strip(),
            old_hash=_parse_hash_token(raw),
            old_hash_raw=raw,
        )


def parse_hash_list_lines(lines: Iterable[str]) -> Iterator[MissingHash]:
    """
    Parse a file containing just Adler32 values (one per line).

    Accepts decimal or 0x-prefixed values and optional C/C++ suffixes (u/ul).
    """
    for line in lines:
        token = line.strip()
        if not token or token.startswith("#"):
            continue
        yield MissingHash(mod="", name="", old_hash=_parse_hash_token(token), old_hash_raw=token)
