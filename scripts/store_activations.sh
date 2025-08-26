#!/usr/bin/env bash
set -euo pipefail

CURRENT_DATETIME=$(date +"%Y%m%d-%H-%M-%S")
OUTPUT_CSV="../run_${CURRENT_DATETIME}.csv"

TMP_LIST=$(mktemp)
TMP_AWK=$(mktemp)
trap 'rm -f "$TMP_LIST" "$TMP_AWK"' EXIT

# Fetch once
wsk -i activation list --limit 200 > "$TMP_LIST"

# Header
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

  # Console summary
  printf("Rows: %d | Avg: %.2f ms | Warm: %d (%.2f ms) | Cold: %d (%.2f ms)\n",
         n, (n?sum/n:0), wn, (wn?wsum/wn:0), cn, (cn?csum/cn:0)) > "/dev/stderr"
}
AWK

# Run awk
awk -v out="$OUTPUT_CSV" -f "$TMP_AWK" "$TMP_LIST"

echo "Data has been written to $OUTPUT_CSV"
