from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _maybe_run(step: str, out_path: Path, force: bool, fn, argv: List[str]) -> None:
    if out_path.exists() and not force:
        print(f"[skip] {step}: {out_path}")
        return
    print(f"[run]  {step}: {out_path}")
    rc = fn(argv)
    if rc != 0:
        raise SystemExit(rc)
    if not out_path.exists():
        raise RuntimeError(f"{step} did not produce expected output: {out_path}")


def _has_anchor_kind(old_missing_sigs_path: Path, kind: str) -> bool:
    import json

    obj = json.loads(old_missing_sigs_path.read_text(encoding="utf-8"))
    for item in obj.get("missing", []):
        for sig in item.get("signatures", []):
            if sig.get("kind") == kind:
                return True
    return False


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "End-to-end CP2077 hash update pipeline.\n"
            "Uses ida-domain in library mode with save_on_close=True to cache IDA databases."
        )
    )
    parser.add_argument("--old-dir", default="old", help="Old build directory (2.3)")
    parser.add_argument("--new-dir", default="new", help="New build directory (2.31)")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--missing-log",
        help="Path to missing-hashes log (e.g. output from cp2077_check_core_framework_hashes.py).",
    )
    src.add_argument(
        "--hashes",
        help="Path to a file containing Adler32 hashes (one per line, 0x... or decimal).",
    )
    parser.add_argument("--out", help="Merged detailed output JSON path.")
    parser.add_argument(
        "--out-simple",
        help="Simple mapping output JSON path: { old_hash: new_hash }",
    )
    parser.add_argument(
        "--cache-dir",
        default=".cp2077_cache",
        help="Directory for intermediate JSON artifacts (signature index, matches, etc).",
    )
    parser.add_argument(
        "--insn-count",
        type=int,
        default=30,
        help="Instruction count used in function signatures.",
    )
    parser.add_argument(
        "--digest-bytes",
        type=int,
        default=16,
        help="blake2b digest size for signature hashing.",
    )
    parser.add_argument(
        "--scan-insns",
        type=int,
        default=180,
        help="For xref resolution: max instructions to scan in candidate functions.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recompute intermediates even if cached JSON exists.",
    )
    args = parser.parse_args(argv)

    old_dir = Path(args.old_dir)
    new_dir = Path(args.new_dir)
    missing_log = Path(args.missing_log) if args.missing_log else None
    hashes_path = Path(args.hashes) if args.hashes else None
    if missing_log and not missing_log.exists():
        raise FileNotFoundError(missing_log)
    if hashes_path and not hashes_path.exists():
        raise FileNotFoundError(hashes_path)

    old_exe = old_dir / "Cyberpunk2077.exe"
    new_exe = new_dir / "Cyberpunk2077.exe"
    old_addresses = old_dir / "cyberpunk2077_addresses.json"
    new_addresses = new_dir / "cyberpunk2077_addresses.json"

    for p in [old_exe, new_exe, old_addresses, new_addresses]:
        if not p.exists():
            raise FileNotFoundError(p)

    cache_dir = Path(args.cache_dir)
    _ensure_dir(cache_dir)

    new_sig_index = cache_dir / "new_sig_index.json"
    old_missing_sigs = cache_dir / "old_missing_sigs.json"
    func_updates = cache_dir / "func_updates.json"
    xref_updates = cache_dir / "xref_updates.json"

    # Import locally so "python cp2077_run_all.py --help" works without ida-domain installed.
    import cp2077_ida_build_sig_index
    import cp2077_ida_export_old_missing_sigs
    import cp2077_ida_resolve_xref_anchors_in_new
    import cp2077_match_missing_hashes
    import cp2077_merge_updates

    _maybe_run(
        "build new signature index",
        new_sig_index,
        args.force,
        cp2077_ida_build_sig_index.main,
        [
            "--exe",
            str(new_exe),
            "--out",
            str(new_sig_index),
            "--insn-count",
            str(args.insn_count),
            "--digest-bytes",
            str(args.digest_bytes),
        ],
    )

    _maybe_run(
        "export old missing signatures",
        old_missing_sigs,
        args.force,
        cp2077_ida_export_old_missing_sigs.main,
        (
            [
                "--exe",
                str(old_exe),
                "--old-addresses",
                str(old_addresses),
                "--missing-log",
                str(missing_log),
                "--out",
                str(old_missing_sigs),
                "--insn-count",
                str(args.insn_count),
                "--digest-bytes",
                str(args.digest_bytes),
            ]
            if missing_log
            else [
                "--exe",
                str(old_exe),
                "--old-addresses",
                str(old_addresses),
                "--hashes",
                str(hashes_path),
                "--out",
                str(old_missing_sigs),
                "--insn-count",
                str(args.insn_count),
                "--digest-bytes",
                str(args.digest_bytes),
            ]
        ),
    )

    if _has_anchor_kind(old_missing_sigs, "func"):
        _maybe_run(
            "match function anchors offline",
            func_updates,
            args.force,
            cp2077_match_missing_hashes.main,
            [
                "--new-addresses",
                str(new_addresses),
                "--new-sig-index",
                str(new_sig_index),
                "--old-missing-sigs",
                str(old_missing_sigs),
                "--out",
                str(func_updates),
            ],
        )
    else:
        func_updates.write_text('{"results":[]}', encoding="utf-8")
        print("[skip] match function anchors offline: no func anchors")

    if _has_anchor_kind(old_missing_sigs, "xref"):
        _maybe_run(
            "resolve xref anchors in new",
            xref_updates,
            args.force,
            cp2077_ida_resolve_xref_anchors_in_new.main,
            [
                "--exe",
                str(new_exe),
                "--new-addresses",
                str(new_addresses),
                "--new-sig-index",
                str(new_sig_index),
                "--old-missing-sigs",
                str(old_missing_sigs),
                "--out",
                str(xref_updates),
                "--scan-insns",
                str(args.scan_insns),
            ],
        )
    else:
        xref_updates.write_text('{"results":[]}', encoding="utf-8")
        print("[skip] resolve xref anchors in new: no xref anchors")

    out_path = Path(args.out)
    simple_path = Path(args.out_simple) if args.out_simple else None
    print(f"[run]  merge results: {out_path}")
    merge_argv = [
        "--func-updates",
        str(func_updates),
        "--xref-updates",
        str(xref_updates),
        "--out",
        str(out_path),
    ]
    if simple_path:
        merge_argv.extend(["--out-simple", str(simple_path)])

    rc = cp2077_merge_updates.main(merge_argv)
    if rc != 0:
        return rc

    print(f"[ok]   wrote {out_path}")
    if simple_path:
        print(f"[ok]   wrote {simple_path}")
    return 0


if __name__ == "__main__":
    # ida-domain often shells out / spawns IDA; keep an explicit __main__ guard.
    raise SystemExit(main())
