from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

from cp2077_hashes.address_list import load_address_list, parse_offset


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline matcher: use NEW signature index + OLD missing signatures to propose old_hash->new_hash updates."
    )
    parser.add_argument("--new-addresses", required=True, help="Path to NEW cyberpunk2077_addresses.json")
    parser.add_argument("--new-sig-index", required=True, help="Path to NEW signature index JSON (from IDA)")
    parser.add_argument("--old-missing-sigs", required=True, help="Path to OLD missing signatures JSON (from IDA)")
    parser.add_argument("--out", required=True, help="Output JSON path")
    args = parser.parse_args(argv)

    new_list = load_address_list(args.new_addresses)
    new_loc_to_hash = new_list.loc_to_hash()

    new_index_json = json.loads(Path(args.new_sig_index).read_text(encoding="utf-8"))
    old_missing_json = json.loads(Path(args.old_missing_sigs).read_text(encoding="utf-8"))

    new_index: Dict[str, List[str]] = new_index_json["index"]

    results = []
    for item in old_missing_json["missing"]:
        old_hash = int(item["old_hash"])
        candidates = []
        for sig_entry in item.get("signatures", []):
            sig = sig_entry["sig"]
            locs = new_index.get(sig, [])
            for off_s in locs:
                sec_idx, sec_off = parse_offset(off_s)
                new_hash = new_loc_to_hash.get((sec_idx, sec_off))
                candidates.append(
                    {
                        "sig": sig,
                        "new_offset": off_s,
                        "new_hash": new_hash,
                    }
                )

        # Prefer candidates that map to a hash present in the new address list.
        good = [c for c in candidates if c["new_hash"] is not None]
        results.append(
            {
                "mod": item.get("mod"),
                "name": item.get("name"),
                "old_hash": old_hash,
                "candidates": good if good else candidates,
                "status": (
                    "matched"
                    if any(c.get("new_hash") is not None for c in candidates)
                    else ("ambiguous_no_hash" if candidates else "no_signature_or_no_match")
                ),
            }
        )

    out = {
        "meta": {
            "new_timestamp": new_list.header.linker_map_timestamp,
            "new_preferred_load_address": new_list.header.preferred_load_address,
        },
        "results": results,
    }

    Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

