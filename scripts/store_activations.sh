#!/usr/bin/env bash
set -euo pipefail

CURRENT_DATETIME=$(date +"%Y%m%d-%H-%M-%S")
OUTPUT_CSV="../run_${CURRENT_DATETIME}.csv"
LOG_FILE="run_summary_sep19.log"

TMP_LIST=$(mktemp)
TMP_AWK=$(mktemp)
trap 'rm -f "$TMP_LIST" "$TMP_AWK"' EXIT

# Fetch ALL activations using --skip loop
limit=200
skip=0
while true; do
    # Grab a batch
    batch=$(mktemp)
    wsk -i activation list --limit $limit --skip $skip > "$batch"

    # Count lines (excluding header)
    nlines=$(($(wc -l < "$batch") - 1))

    if (( nlines <= 0 )); then
        rm -f "$batch"
        break
    fi

    if (( skip == 0 )); then
        # Keep the header from the first call
        cat "$batch" >> "$TMP_LIST"
    else
        # Skip header for subsequent calls
        tail -n +2 "$batch" >> "$TMP_LIST"
    fi

    rm -f "$batch"

    # Move to next page
    skip=$((skip + limit))
done

# Header for CSV
echo "Datetime,Activation ID,Kind,Start,Duration,Status,Entity" > "$OUTPUT_CSV"

# AWK program (stored in a temp file to avoid quoting issues)
cat > "$TMP_AWK" <<'AWK'
function to_ms(v) {
  if (v ~ /ms$/) { sub(/ms$/, "", v); return v + 0 }
  if (v ~ /s$/)  { sub(/s$/,  "", v); return (v + 0) * 1000 }
  return v + 0
}
NR > 1 {
  # CSV row (combine date+time in first column from `wsk activation list`)
  print $1" "$2","$3","$4","$5","$6","$7","$8 >> out

  ms = to_ms($6)
  sum += ms; n++

  if ($5 == "warm") { wsum += ms; wn++ }
  else if ($5 == "cold") { csum += ms; cn++ }
}
END {
  print "" >> out
  printf("Average(ms),%.2f\n", (n ? sum/n : 0)) >> out
  printf("Warm Starts,%d\n", wn) >> out
  printf("Cold Starts,%d\n", cn) >> out
  printf("Average Warm (ms),%.2f\n", (wn ? wsum/wn : 0)) >> out
  printf("Average Cold (ms),%.2f\n", (cn ? csum/cn : 0)) >> out

  # Console + log summary (no timestamp prefix)
  summary = sprintf("Rows: %d | Avg: %.2f ms | Warm: %d (%.2f ms) | Cold: %d (%.2f ms)",
                    n, (n?sum/n:0), wn, (wn?wsum/wn:0), cn, (cn?csum/cn:0))

  print summary > "/dev/stderr"
  print summary >> "run_summary_sep19.log"
}
AWK

# Run awk
awk -v out="$OUTPUT_CSV" -f "$TMP_AWK" "$TMP_LIST"

# Final line, also append to log
echo "Data has been written to $OUTPUT_CSV" | tee -a "$LOG_FILE"
