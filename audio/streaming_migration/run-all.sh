#!/usr/bin/env bash
# Runs spotify-csv-to-m3u.py over every CSV in a directory (default: data/exportify).
# Usage: ./run-all.sh [csv_dir]
set -uo pipefail

scriptDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pyScript="$scriptDir/spotify-csv-to-m3u.py"
csvDir="${1:-$scriptDir/data/exportify}"

if [[ ! -d "$csvDir" ]]; then
    echo "CSV directory not found: $csvDir" >&2
    exit 1
fi

# Run from scriptDir so meta.json (the ffprobe cache) is shared across all CSVs
# in this batch instead of being rebuilt per invocation.
cd "$scriptDir" || exit 1

count=0
failed=()

while IFS= read -r -d '' csv; do
    count=$((count + 1))
    echo "=== [$count] $(basename "$csv") ==="
    if ! python3 "$pyScript" "$csv"; then
        echo "FAILED: $csv" >&2
        failed+=("$csv")
    fi
    echo
done < <(find "$csvDir" -maxdepth 1 -type f -name '*.csv' -print0 | sort -z)

echo "Processed $count CSV file(s)."
if [[ ${#failed[@]} -gt 0 ]]; then
    echo "Failed (${#failed[@]}):"
    printf '  %s\n' "${failed[@]}"
    exit 1
fi
