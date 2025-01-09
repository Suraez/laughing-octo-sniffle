#!/bin/bash

# Check if the output file path is provided as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <output_csv_path>"
  exit 1
fi

# Output CSV file path from CLI argument
OUTPUT_CSV="$1"

# Write header to the CSV file
echo "Datetime,Activation ID,Kind,Start,Duration,Status,Entity" > "$OUTPUT_CSV"

# Append formatted data from wsk command to the CSV
wsk -i activation list --limit 200 | awk '
NR > 1 { print $1" "$2","$3","$4","$5","$6","$7","$8 }' >> "$OUTPUT_CSV"

echo "Data has been written to $OUTPUT_CSV"
