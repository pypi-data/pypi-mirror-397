from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cp2077_hashes.address_list import load_address_list, parse_offset
from cp2077_hashes.ida_signatures import IdaLocalBackend
from cp2077_hashes.pe_sections import read_pe_sections, rva_to_offset_string


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resolve xref-based anchors against the NEW binary using ida-domain. "
        "Input: OLD missing signatures JSON (with kind=xref entries) and NEW signature index."
    )
    parser.add_argument("--exe", required=True, help="Path to NEW Cyberpunk2077.exe")
    parser.add_argument(
        "--new-addresses",
        required=True,
        help="Path to NEW cyberpunk2077_addresses.json",
    )
    parser.add_argument(
        "--new-sig-index",
        required=True,
        help="Path to NEW signature index JSON (from IDA)",
    )
    parser.add_argument(
        "--old-missing-sigs",
        required=True,
        help="Path to OLD missing signatures JSON (from IDA)",
    )
    parser.add_argument("--out", required=True, help="Output JSON path")
    parser.add_argument(
        "--scan-insns",
        type=int,
        default=180,
        help="Max instructions to scan in each candidate function.",
    )
    args = parser.parse_args(argv)

    new_list = load_address_list(args.new_addresses)
    new_loc_to_hash = new_list.loc_to_hash()

    new_sig_index = json.loads(Path(args.new_sig_index).read_text(encoding="utf-8"))
    sig_to_func_offsets: Dict[str, List[str]] = new_sig_index["index"]

    old_missing = json.loads(Path(args.old_missing_sigs).read_text(encoding="utf-8"))

    exe_path = Path(args.exe)
    sections = read_pe_sections(exe_path)

    try:
        from ida_domain import Database
        from ida_domain.database import IdaCommandOptions
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "ida-domain is required. Install it with `pip install ida-domain` and set IDADIR to your IDA install."
        ) from e

    ida_opts = IdaCommandOptions(auto_analysis=True, new_database=False)
    results = []

    with Database.open(str(exe_path), args=ida_opts, save_on_close=True) as _db:
        ida = IdaLocalBackend()
        imagebase = ida.get_imagebase()

        for item in old_missing.get("missing", []):
            old_hash = int(item["old_hash"])
            anchors = item.get("signatures", [])
            xref_anchors = [a for a in anchors if a.get("kind") == "xref"]
            out_candidates = []

            for a in xref_anchors:
                sig = a["sig"]
                insn_idx = int(a["insn_idx"])
                expected_mnem = str(a.get("mnem") or "")
                op_index = int(a["op_index"])

                for func_off in sig_to_func_offsets.get(sig, []):
                    sec_idx, sec_off = parse_offset(func_off)
                    rva = sections[sec_idx - 1].virtual_address + sec_off
                    func_start_ea = imagebase + rva

                    insn_eas = ida.iter_insn_eas(
                        func_start_ea, insn_count=max(args.scan_insns, insn_idx + 1)
                    )
                    if insn_idx >= len(insn_eas):
                        continue
                    ea = insn_eas[insn_idx]
                    if expected_mnem and ida.get_insn_mnem(ea) != expected_mnem:
                        # Fallback: allow scanning nearby window for the expected mnemonic at same operand index.
                        window = range(
                            max(0, insn_idx - 6), min(len(insn_eas), insn_idx + 7)
                        )
                        found = None
                        for j in window:
                            if ida.get_insn_mnem(insn_eas[j]) == expected_mnem:
                                found = insn_eas[j]
                                break
                        if found is None:
                            continue
                        ea = found

                    try:
                        target_ea = ida.get_operand_value(ea, op_index)
                    except Exception:
                        continue
                    if not target_ea or target_ea < imagebase:
                        continue

                    target_rva = target_ea - imagebase
                    target_off = rva_to_offset_string(sections, target_rva)
                    if not target_off:
                        continue
                    t_sec, t_off = parse_offset(target_off)
                    new_hash = new_loc_to_hash.get((t_sec, t_off))
                    out_candidates.append(
                        {
                            "sig": sig,
                            "new_func_offset": func_off,
                            "xref_insn_mnem": ida.get_insn_mnem(ea),
                            "xref_op_index": op_index,
                            "new_target_offset": target_off,
                            "new_hash": new_hash,
                        }
                    )

            # Prefer candidates where the resolved target offset is actually in the new address list.
            good = [c for c in out_candidates if c.get("new_hash") is not None]
            results.append(
                {
                    "mod": item.get("mod"),
                    "name": item.get("name"),
                    "old_hash": old_hash,
                    "status": (
                        "matched"
                        if good
                        else (
                            "ambiguous_no_hash" if out_candidates else "no_xref_match"
                        )
                    ),
                    "candidates": good if good else out_candidates,
                }
            )

    out = {
        "meta": {
            "new_timestamp": new_list.header.linker_map_timestamp,
            "new_preferred_load_address": new_list.header.preferred_load_address,
            "exe": str(exe_path),
        },
        "results": results,
    }
    Path(args.out).write_text(
        json.dumps(out, indent=2, sort_keys=False), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
