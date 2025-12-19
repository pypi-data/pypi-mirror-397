from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Mapping, Optional, Tuple


OffsetKey = Tuple[int, int]  # (section_index, section_relative_offset)


@dataclass(frozen=True)
class AddressEntry:
    adler32: int
    offset: OffsetKey
    sha256: str
    symbol: Optional[str] = None


@dataclass(frozen=True)
class AddressListHeader:
    linker_map_timestamp: Optional[str]
    preferred_load_address: Optional[int]
    code_constant_offset: Optional[int]


@dataclass
class AddressList:
    header: AddressListHeader
    entries: List[AddressEntry]

    def hash_set(self) -> set[int]:
        return {e.adler32 for e in self.entries}

    def loc_to_hash(self) -> Dict[OffsetKey, int]:
        # Note: if duplicates exist (multiple hashes at same offset), last wins.
        # In practice offsets appear to be unique; we keep behavior explicit.
        return {e.offset: e.adler32 for e in self.entries}

    def hash_to_locs(self) -> Dict[int, List[OffsetKey]]:
        out: Dict[int, List[OffsetKey]] = {}
        for e in self.entries:
            out.setdefault(e.adler32, []).append(e.offset)
        return out

    def hash_to_best_symbol(self) -> Dict[int, str]:
        out: Dict[int, str] = {}
        for e in self.entries:
            if e.symbol:
                out.setdefault(e.adler32, e.symbol)
        return out


def _parse_hex_int(value: str) -> int:
    value = value.strip()
    if value.lower().startswith("0x"):
        return int(value, 16)
    return int(value, 16)


def parse_offset(offset: str) -> OffsetKey:
    # JSON format: "0001:001447c8"
    sec_s, off_s = offset.split(":", 1)
    return int(sec_s, 16), int(off_s, 16)


def load_address_list(path: str | Path) -> AddressList:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    header = AddressListHeader(
        linker_map_timestamp=data.get("Linker map timestamp"),
        preferred_load_address=_parse_hex_int(data["Preferred load address"])
        if "Preferred load address" in data and data["Preferred load address"] is not None
        else None,
        code_constant_offset=int(data["Code constant offset"])
        if "Code constant offset" in data and data["Code constant offset"] is not None
        else None,
    )

    entries: List[AddressEntry] = []
    for item in data.get("Addresses", []):
        # In the files you provided, these are strings.
        adler32 = int(item["hash"])
        sha256 = str(item["secondary hash"])
        offset = parse_offset(item["offset"])
        symbol = item.get("symbol")
        entries.append(AddressEntry(adler32=adler32, offset=offset, sha256=sha256, symbol=symbol))

    return AddressList(header=header, entries=entries)

