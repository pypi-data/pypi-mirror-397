from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional

from cp2077_hashes.ida_signatures import IdaLocalBackend, Signature
from cp2077_hashes.pe_sections import read_pe_sections, rva_to_offset_string


def _sig_hash(sig: Signature, digest_bytes: int) -> str:
    h = hashlib.blake2b(digest_size=digest_bytes)
    for token in sig:
        h.update(token.encode("utf-8", errors="replace"))
        h.update(b"\n")
    return h.hexdigest()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a signature index of function starts in .text using ida-domain (library mode)."
    )
    parser.add_argument("--exe", required=True, help="Path to NEW Cyberpunk2077.exe")
    parser.add_argument(
        "--out", required=True, help="Output JSON path for the signature index."
    )
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

    try:
        from ida_domain import Database
        from ida_domain.database import IdaCommandOptions
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "ida-domain is required. Install it with `pip install ida-domain` and set IDADIR to your IDA install."
        ) from e

    ida_opts = IdaCommandOptions(auto_analysis=True, new_database=False)
    index: Dict[str, List[str]] = {}
    imagebase: Optional[int] = None

    with Database.open(str(exe_path), args=ida_opts, save_on_close=True) as _db:
        ida = IdaLocalBackend()
        imagebase = ida.get_imagebase()

        for func_start in ida.iter_function_starts_in_text():
            rva = func_start - imagebase
            off_s = rva_to_offset_string(sections, rva)
            if off_s is None:
                continue
            sig = ida.signature_at(func_start, insn_count=args.insn_count)
            if not sig:
                continue
            key = _sig_hash(sig, digest_bytes=args.digest_bytes)
            index.setdefault(key, []).append(off_s)

    out = {
        "meta": {
            "exe": str(exe_path),
            "imagebase": imagebase,
            "insn_count": args.insn_count,
            "hash": f"blake2b-{args.digest_bytes}",
            "entries": sum(len(v) for v in index.values()),
            "unique_signatures": len(index),
        },
        "index": index,
    }

    Path(args.out).write_text(
        json.dumps(out, indent=2, sort_keys=False), encoding="utf-8"
    )
    print(f"Wrote {args.out} with {out['meta']['entries']} functions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
