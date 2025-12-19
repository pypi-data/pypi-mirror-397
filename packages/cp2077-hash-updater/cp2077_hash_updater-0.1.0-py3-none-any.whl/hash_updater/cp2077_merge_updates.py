from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _load_results(path: Optional[str]) -> List[Dict[str, Any]]:
    if not path:
        return []
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(obj.get("results", []))


def _canonicalize_candidates(item: Dict[str, Any], method: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for c in item.get("candidates", []):
        new_hash = c.get("new_hash")
        if new_hash is None:
            continue
        try:
            new_hash_int = int(new_hash)
        except Exception:
            continue

        if method == "func":
            new_offset = c.get("new_offset")
        else:
            # xref-based resolver yields the *target* offset; that's the symbol location we want.
            new_offset = c.get("new_target_offset")

        if not isinstance(new_offset, str) or ":" not in new_offset:
            new_offset = None

        out.append(
            {
                "method": method,
                "new_hash": new_hash_int,
                "new_offset": new_offset,
                "details": c,
            }
        )
    return out


def _pick_best(candidates: List[Dict[str, Any]]) -> Tuple[str, Optional[int]]:
    """
    Pick best hash:
    - Prefer xref-based evidence over function-start signature matches.
    - Prefer hashes that appear multiple times (multiple anchors).
    """
    if not candidates:
        return "unresolved", None

    by_hash: Dict[int, Dict[str, Any]] = {}
    for c in candidates:
        h = int(c["new_hash"])
        method = str(c.get("method") or "")
        method_priority = 2 if method == "xref" else 1
        bucket = by_hash.setdefault(h, {"hash": h, "count": 0, "best_method_priority": 0})
        bucket["count"] += 1
        bucket["best_method_priority"] = max(bucket["best_method_priority"], method_priority)

    ranked = sorted(
        by_hash.values(),
        key=lambda b: (int(b["best_method_priority"]), int(b["count"]), int(b["hash"])),
        reverse=True,
    )

    best = ranked[0]
    tied = [r for r in ranked if (r["best_method_priority"], r["count"]) == (best["best_method_priority"], best["count"])]
    if len(tied) > 1:
        return "ambiguous", None
    return "matched", int(best["hash"])


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Merge func-based and xref-based hash update proposals into one report.")
    parser.add_argument("--func-updates", help="Output of cp2077_match_missing_hashes.py (func signature matches).")
    parser.add_argument("--xref-updates", help="Output of cp2077_ida_resolve_xref_anchors_in_new.py (xref matches).")
    parser.add_argument("--out", required=True, help="Output JSON path.")
    parser.add_argument(
        "--out-simple",
        help="Optional output JSON path for a simple mapping: { old_hash: new_hash } (only unique matches).",
    )
    args = parser.parse_args(argv)

    func_results = _load_results(args.func_updates)
    xref_results = _load_results(args.xref_updates)

    by_old: Dict[int, Dict[str, Any]] = {}

    def ingest(items: List[Dict[str, Any]], method: str) -> None:
        for item in items:
            try:
                old_hash = int(item["old_hash"])
            except Exception:
                continue
            merged = by_old.setdefault(
                old_hash,
                {
                    "old_hash": old_hash,
                    "mod": None,
                    "name": None,
                    "candidates": [],
                },
            )
            if not merged.get("mod") and item.get("mod"):
                merged["mod"] = item.get("mod")
            if not merged.get("name") and item.get("name"):
                merged["name"] = item.get("name")
            merged["candidates"].extend(_canonicalize_candidates(item, method=method))

    ingest(func_results, method="func")
    ingest(xref_results, method="xref")

    results: List[Dict[str, Any]] = []
    for old_hash in sorted(by_old.keys()):
        merged = by_old[old_hash]
        # Deduplicate by (new_hash, new_offset, method)
        seen = set()
        uniq_candidates = []
        for c in merged["candidates"]:
            key = (c["new_hash"], c.get("new_offset"), c.get("method"))
            if key in seen:
                continue
            seen.add(key)
            uniq_candidates.append(c)
        merged["candidates"] = uniq_candidates

        status, picked = _pick_best(uniq_candidates)
        merged["status"] = status
        merged["new_hash"] = picked
        results.append(merged)

    out = {"results": results}
    Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=False), encoding="utf-8")

    if args.out_simple:
        simple: Dict[str, int] = {}
        for r in results:
            if r.get("status") == "matched" and r.get("new_hash") is not None:
                simple[str(int(r["old_hash"]))] = int(r["new_hash"])
        Path(args.out_simple).write_text(json.dumps(simple, indent=2, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
