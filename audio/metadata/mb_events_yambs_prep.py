#!/usr/bin/env python3
"""Prepare events CSV for yambs MusicBrainz batch upload.

Strips non-yambs helper columns and prints the yambs invocation command.
Install yambs: go install codeberg.org/derat/yambs@latest
"""

import csv
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DEFAULT_INPUT = SCRIPT_DIR / "data" / "docents_events_full_with_supporting_acts.csv"

YAMBS_FIELDS = [
    "name", "begin_date", "end_date", "type", "cancelled",
    "disambiguation", "setlist", "time", "edit_note",
    "rel0_target", "rel0_type", "rel0_target_credit",
    "rel1_target", "rel1_type", "rel1_target_credit",
    "rel2_target", "rel2_type", "rel2_target_credit",
    "rel3_target", "rel3_type", "rel3_target_credit",
    "rel4_target", "rel4_type", "rel4_target_credit",
    "rel5_target", "rel5_type", "rel5_target_credit",
    "rel6_target", "rel6_type", "rel6_target_credit",
    "rel7_target", "rel7_type", "rel7_target_credit",
]


def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = (
        Path(sys.argv[2])
        if len(sys.argv) > 2
        else input_path.parent / (input_path.stem + "_yambs.csv")
    )

    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    missing = [col for col in YAMBS_FIELDS if col not in rows[0]]
    if missing:
        print(f"ERROR: missing expected columns: {missing}", file=sys.stderr)
        sys.exit(1)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=YAMBS_FIELDS, extrasaction="ignore",
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in YAMBS_FIELDS})

    fields_arg = ",".join(YAMBS_FIELDS)

    print(f"Wrote {len(rows)} events → {output_path}")
    print()
    print("=" * 60)
    print("INSTALL yambs (requires Go):")
    print("  go install codeberg.org/derat/yambs@latest")
    print()
    print("RUN (beta server — safe for testing):")
    print(f"  yambs -type event -format csv \\")
    print(f"    -server beta.musicbrainz.org \\")
    print(f"    -fields '{fields_arg}' \\")
    print(f"    '{output_path}'")
    print()
    print("RUN (production — when ready):")
    print(f"  yambs -type event -format csv \\")
    print(f"    -fields '{fields_arg}' \\")
    print(f"    '{output_path}'")
    print("=" * 60)
    print()
    print("CAVEATS:")
    print("  - rel*_target values are plain text names (not MBIDs).")
    print("    yambs will try to match them to existing MB entities.")
    print("    Unrecognized venues/artists need manual disambiguation in the UI.")
    print("  - Review output CSV before submitting.")
    print("  - yambs opens a browser window per batch; confirm each edit there.")


if __name__ == "__main__":
    main()
