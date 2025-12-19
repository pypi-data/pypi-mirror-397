from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct
from typing import List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class PeSection:
    name: str
    virtual_address: int
    virtual_size: int
    raw_ptr: int
    raw_size: int


class PeFormatError(RuntimeError):
    pass


def _u16(b: bytes, off: int) -> int:
    return struct.unpack_from("<H", b, off)[0]


def _u32(b: bytes, off: int) -> int:
    return struct.unpack_from("<I", b, off)[0]


def read_pe_sections(path: str | Path) -> List[PeSection]:
    """
    Read PE section headers in file order.

    This is used to map JSON offsets `(section_index, section_relative_offset)` to RVAs:
      rva = sections[section_index - 1].virtual_address + section_relative_offset
    """
    path = Path(path)
    blob = path.read_bytes()

    if len(blob) < 0x100:
        raise PeFormatError("File too small to be a PE.")

    if blob[:2] != b"MZ":
        raise PeFormatError("Missing MZ header.")

    e_lfanew = _u32(blob, 0x3C)
    if e_lfanew + 4 + 20 > len(blob):
        raise PeFormatError("Invalid e_lfanew.")

    if blob[e_lfanew : e_lfanew + 4] != b"PE\x00\x00":
        raise PeFormatError("Missing PE signature.")

    file_header_off = e_lfanew + 4
    number_of_sections = _u16(blob, file_header_off + 2)
    size_of_optional_header = _u16(blob, file_header_off + 16)

    optional_header_off = file_header_off + 20
    section_table_off = optional_header_off + size_of_optional_header
    section_header_size = 40

    sections: List[PeSection] = []
    for i in range(number_of_sections):
        off = section_table_off + i * section_header_size
        if off + section_header_size > len(blob):
            raise PeFormatError("Section table truncated.")

        name = blob[off : off + 8].split(b"\x00", 1)[0].decode("ascii", "replace")
        virtual_size = _u32(blob, off + 8)
        virtual_address = _u32(blob, off + 12)
        raw_size = _u32(blob, off + 16)
        raw_ptr = _u32(blob, off + 20)

        sections.append(
            PeSection(
                name=name,
                virtual_address=virtual_address,
                virtual_size=virtual_size,
                raw_ptr=raw_ptr,
                raw_size=raw_size,
            )
        )

    return sections


def offset_key_to_rva(sections: Sequence[PeSection], sec_idx: int, sec_off: int) -> int:
    if sec_idx <= 0 or sec_idx > len(sections):
        raise ValueError(f"Section index {sec_idx} out of range (1..{len(sections)}).")
    return sections[sec_idx - 1].virtual_address + sec_off


def rva_to_offset_key(sections: Sequence[PeSection], rva: int) -> Optional[Tuple[int, int]]:
    """
    Convert an RVA into `(section_index, section_relative_offset)` using section table order (1-based).
    """
    for idx, s in enumerate(sections, start=1):
        start = s.virtual_address
        end = start + max(s.virtual_size, s.raw_size)
        if start <= rva < end:
            return idx, rva - start
    return None


def rva_to_offset_string(sections: Sequence[PeSection], rva: int) -> Optional[str]:
    key = rva_to_offset_key(sections, rva)
    if key is None:
        return None
    sec_idx, sec_off = key
    return f"{sec_idx:04x}:{sec_off:08x}"
