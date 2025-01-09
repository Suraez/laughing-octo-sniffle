#!/bin/bash

# Get the current datetime in the desired format
CURRENT_DATETIME=$(date +"%Y%m%d-%H-%M-%S")

# Output CSV file with datetime in the name
OUTPUT_CSV="../run_${CURRENT_DATETIME}.csv"

# Write header to the CSV file
echo "Datetime,Activation ID,Kind,Start,Duration,Status,Entity" > "$OUTPUT_CSV"

# Append formatted data from wsk command to the CSV
wsk -i activation list --limit 200 | awk '
NR > 1 { print $1" "$2","$3","$4","$5","$6","$7","$8 }' >> "$OUTPUT_CSV"

echo "Data has been written to $OUTPUT_CSV"
