#!/bin/bash

# Input file
DATASET="/home/suraj/projects/laughing-octo-sniffle/invocation_dataset/trace3.csv"
OUTPUT_MAPPING="/home/suraj/projects/laughing-octo-sniffle/function_mapping.csv"

# Reversed Action List
declare -a ACTION_LIST=(
    "ac"
    "is"
    "oi"
    "dh"
    "ul"
    "tn"
    "fc"
    "ir"
    "sa"
    "dv"
    "md"
    "gb"
    "gm"
    "gp"
    "dt"
    "dl"
    "dq"
    "ds"
    "dg"
    "EndExperiment"
)

# Create mapping between HashFunction values and Action List
echo "HashFunction,Action" > "$OUTPUT_MAPPING"
declare -A hash_function_map
hash_index=0
total_actions=${#ACTION_LIST[@]}

# Build the HashFunction-to-Action mapping
while IFS=, read -r -a row; do
    # Skip header
    if [[ "${row[0]}" == "HashOwner" || "${row[1]}" == "HashApp" || "${row[2]}" == "HashFunction" ]]; then
        continue
    fi

    # Extract HashFunction from the third column
    HASH_FUNCTION="${row[2]}"
    if [[ -n "$HASH_FUNCTION" && -z "${hash_function_map[$HASH_FUNCTION]}" ]]; then
        # Map HashFunction to the current action
        hash_function_map[$HASH_FUNCTION]="${ACTION_LIST[$hash_index]}"
        echo "$HASH_FUNCTION,${ACTION_LIST[$hash_index]}" >> "$OUTPUT_MAPPING"
        
        # Increment index and wrap around if needed
        ((hash_index++))
        hash_index=$((hash_index % total_actions))
    fi
done < "$DATASET"

echo "Mapping saved to $OUTPUT_MAPPING."

# Initialize invocation counter
invocation_count=0

# Function to invoke actions based on the dataset
invoke_functions() {
    # Iterate over columns 5 to 14 (named 1 to 10)
    for column in {5..14}; do
        MINUTE=$((column - 4))  # Map column index to minute number
        echo "Processing minute $MINUTE (column $column)..."

        # Iterate over all rows in the dataset
        while IFS=, read -r -a row; do
            # Skip header
            if [[ "${row[0]}" == "HashOwner" || "${row[1]}" == "HashApp" || "${row[2]}" == "HashFunction" ]]; then
                continue
            fi

            # Extract HashFunction and current column value
            HASH_FUNCTION="${row[2]}"
            COLUMN_VALUE="${row[$column-1]}"

            # If column value is greater than 0, invoke the function equal to the cell value
            if [[ "$COLUMN_VALUE" -gt 0 ]]; then
                FUNC="${hash_function_map[$HASH_FUNCTION]}"
                if [[ -n "$FUNC" ]]; then
                    for ((i = 1; i <= COLUMN_VALUE; i++)); do
                        echo "Invoking function: wsk -i action invoke $FUNC (Minute: $MINUTE) - Invocation $i of $COLUMN_VALUE"
                        wsk -i action invoke "$FUNC" --blocking > /dev/null 2>&1
                        ((invocation_count++))  # Increment the counter
                        # sleep 0.5  # Sleep for 0.5 seconds
                    done
                fi
            fi
        done < "$DATASET"
    done
}

# Start invocation
echo "Starting function invocations based on the dataset..."
invoke_functions

# Output the total number of invocations
echo "Function invocation complete."
echo "Total number of invocations: $invocation_count"
