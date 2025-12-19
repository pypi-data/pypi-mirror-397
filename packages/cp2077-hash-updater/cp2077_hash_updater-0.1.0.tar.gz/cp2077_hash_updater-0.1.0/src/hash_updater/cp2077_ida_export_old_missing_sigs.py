from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional

from cp2077_hashes.address_list import load_address_list
from cp2077_hashes.ida_signatures import IdaLocalBackend, Signature
from cp2077_hashes.missing_log import parse_hash_list_lines, parse_missing_log_lines
from cp2077_hashes.pe_sections import offset_key_to_rva, read_pe_sections


def _sig_hash(sig: Signature, digest_bytes: int) -> str:
    h = hashlib.blake2b(digest_size=digest_bytes)
    for token in sig:
        h.update(token.encode("utf-8", errors="replace"))
        h.update(b"\n")
    return h.hexdigest()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute signature hashes for missing mod hashes using ida-domain (library mode)."
    )
    parser.add_argument("--exe", required=True, help="Path to OLD Cyberpunk2077.exe")
    parser.add_argument(
        "--old-addresses",
        required=True,
        help="Path to OLD cyberpunk2077_addresses.json",
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--missing-log", help="Path to missing-hashes log output")
    src.add_argument("--hashes", help="Path to a file of Adler32 hashes (one per line)")
    parser.add_argument("--out", required=True, help="Output JSON path")
    parser.add_argument(
        "--insn-count",
        type=int,
        default=30,
        help="Number of instructions per signature.",
    )
    parser.add_argument(
        "--digest-bytes", type=int, default=16, help="blake2b digest length in bytes."
    )
    args = parser.parse_args(argv)

    exe_path = Path(args.exe)
    sections = read_pe_sections(exe_path)
    old_list = load_address_list(args.old_addresses)
    old_hash_to_locs = old_list.hash_to_locs()

    if args.missing_log:
        missing_lines = (
            Path(args.missing_log)
            .read_text(encoding="utf-8", errors="replace")
            .splitlines()
        )
        missing = list(parse_missing_log_lines(missing_lines))
        source = {"kind": "missing_log", "path": str(args.missing_log)}
    else:
        hash_lines = Path(args.hashes).read_text(encoding="utf-8", errors="replace").splitlines()
        missing = list(parse_hash_list_lines(hash_lines))
        source = {"kind": "hashes", "path": str(args.hashes)}

    try:
        from ida_domain import Database
        from ida_domain.database import IdaCommandOptions
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "ida-domain is required. Install it with `pip install ida-domain` and set IDADIR to your IDA install."
        ) from e

    ida_opts = IdaCommandOptions(auto_analysis=True, new_database=False)
    results = []
    imagebase: Optional[int] = None
    with Database.open(str(exe_path), args=ida_opts, save_on_close=True) as _db:
        ida = IdaLocalBackend()
        imagebase = ida.get_imagebase()
        import idautils

        for mh in missing:
            locs = old_hash_to_locs.get(mh.old_hash, [])
            sigs: List[Dict[str, str]] = []
            for sec_idx, sec_off in locs:
                rva = offset_key_to_rva(sections, sec_idx, sec_off)
                ea = imagebase + rva
                section_name = (
                    sections[sec_idx - 1].name if 0 < sec_idx <= len(sections) else None
                )

                # If this location is in executable code, treat it as a function anchor.
                if section_name == ".text":
                    func_start = ida.get_function_start(ea) or ea
                    sig = ida.signature_at(func_start, insn_count=args.insn_count)
                    if not sig:
                        continue
                    sigs.append(
                        {
                            "kind": "func",
                            "old_offset": f"{sec_idx:04x}:{sec_off:08x}",
                            "sig": _sig_hash(sig, digest_bytes=args.digest_bytes),
                        }
                    )
                    continue

                # Otherwise (.rdata/.data/etc), anchor via xrefs from code.
                xref_anchors = 0
                for xref in idautils.XrefsTo(int(ea)):
                    from_ea = int(getattr(xref, "frm", getattr(xref, "from", 0)))
                    if not from_ea:
                        continue
                    from_func = ida.get_function_start(from_ea)
                    if not from_func:
                        continue

                    # Locate the instruction ordinal within the function (so we can find it again in new).
                    insn_eas = ida.iter_insn_eas(
                        from_func, insn_count=max(args.insn_count, 120)
                    )
                    try:
                        insn_idx = insn_eas.index(from_ea)
                    except ValueError:
                        continue

                    # Identify which operand references the target EA.
                    op_index: Optional[int] = None
                    for i in range(3):
                        try:
                            if ida.get_operand_value(from_ea, i) == int(ea):
                                op_index = i
                                break
                        except Exception:
                            break
                    if op_index is None:
                        continue

                    func_sig = ida.signature_at(from_func, insn_count=args.insn_count)
                    if not func_sig:
                        continue

                    sigs.append(
                        {
                            "kind": "xref",
                            "old_offset": f"{sec_idx:04x}:{sec_off:08x}",
                            "sig": _sig_hash(func_sig, digest_bytes=args.digest_bytes),
                            "insn_idx": insn_idx,
                            "mnem": ida.get_insn_mnem(from_ea),
                            "op_index": op_index,
                        }
                    )
                    xref_anchors += 1
                    if xref_anchors >= 20:
                        break

            results.append(
                {
                    "mod": mh.mod,
                    "name": mh.name,
                    "old_hash": mh.old_hash,
                    "old_hash_raw": mh.old_hash_raw,
                    "signatures": sigs,
                }
            )

    out = {
        "meta": {
            "exe": str(exe_path),
            "imagebase": imagebase,
            "insn_count": args.insn_count,
            "hash": f"blake2b-{args.digest_bytes}",
            "missing_count": len(results),
            "source": source,
        },
        "missing": results,
    }

    Path(args.out).write_text(
        json.dumps(out, indent=2, sort_keys=False), encoding="utf-8"
    )
    print(f"Wrote {args.out} with {len(results)} missing hashes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
