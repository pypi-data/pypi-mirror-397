from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cp2077_hashes.address_list import AddressList, OffsetKey, load_address_list
from cp2077_hashes.missing_log import MissingHash, parse_missing_log_lines
from cp2077_hashes.pe_sections import offset_key_to_rva, read_pe_sections


def _load_missing_hashes(path: Path) -> List[MissingHash]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return list(parse_missing_log_lines(lines))


def _parse_hash_list(path: Path) -> List[int]:
    hashes: List[int] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        hashes.append(int(line, 0))
    return hashes


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Attempt to map missing Adler32 hashes from old->new CP2077 builds using address lists (and optionally IDA signatures)."
    )
    parser.add_argument("--old-dir", default="old", help="Directory with old Cyberpunk2077.exe and cyberpunk2077_addresses.json")
    parser.add_argument("--new-dir", default="new", help="Directory with new Cyberpunk2077.exe and cyberpunk2077_addresses.json")
    parser.add_argument(
        "--missing-log",
        type=str,
        help="Path to a log containing lines like: 'Mod: Failed to find NAME hash! Old: 123ul'",
    )
    parser.add_argument(
        "--hashes",
        type=str,
        help="Path to a file containing Adler32 hashes (one per line, 0x... or decimal).",
    )
    parser.add_argument("--out", default="hash_updates.json", help="Output JSON path.")
    parser.add_argument(
        "--no-ida",
        action="store_true",
        help="Only produce a JSON-only report (missing hashes + old locations).",
    )

    args = parser.parse_args(argv)

    old_dir = Path(args.old_dir)
    new_dir = Path(args.new_dir)
    old_json = old_dir / "cyberpunk2077_addresses.json"
    new_json = new_dir / "cyberpunk2077_addresses.json"

    old_list = load_address_list(old_json)
    new_list = load_address_list(new_json)

    new_hashes = new_list.hash_set()
    old_hash_to_locs = old_list.hash_to_locs()
    new_loc_to_hash = new_list.loc_to_hash()
    old_symbols = old_list.hash_to_best_symbol()

    missing: List[Tuple[int, Optional[str], Optional[str]]] = []
    if args.missing_log:
        for mh in _load_missing_hashes(Path(args.missing_log)):
            missing.append((mh.old_hash, mh.name, mh.mod))
    if args.hashes:
        for h in _parse_hash_list(Path(args.hashes)):
            missing.append((h, None, None))

    if not missing:
        parser.error("Provide --missing-log and/or --hashes.")

    # Deduplicate while preserving order
    seen = set()
    missing_hashes: List[Tuple[int, Optional[str], Optional[str]]] = []
    for h, name, mod in missing:
        if h in seen:
            continue
        seen.add(h)
        missing_hashes.append((h, name, mod))

    report: Dict[str, object] = {
        "old": {"timestamp": old_list.header.linker_map_timestamp, "preferred_load_address": old_list.header.preferred_load_address},
        "new": {"timestamp": new_list.header.linker_map_timestamp, "preferred_load_address": new_list.header.preferred_load_address},
        "results": [],
    }

    for old_hash, name, mod in missing_hashes:
        locs = old_hash_to_locs.get(old_hash, [])
        if not locs:
            status = "missing_in_old_json"
        elif old_hash in new_hashes:
            status = "still_present_in_new"
        else:
            status = "missing_in_new"
        entry = {
            "old_hash": old_hash,
            "status": status,
            "name": name or old_symbols.get(old_hash),
            "mod": mod,
            "old_offsets": [f"{sec:04x}:{off:08x}" for sec, off in locs],
            "new_hash_candidates": [],
        }
        report["results"].append(entry)

    out_path = Path(args.out)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=False), encoding="utf-8")

    if args.no_ida:
        return 0

    # IDA signature matching is intentionally not executed here because it requires IDA + ida-domain setup.
    # This script currently emits the trimmed worklist, which you can feed into an IDA-driven pipeline.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
