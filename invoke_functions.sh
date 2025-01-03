#!/bin/bash

# Input file
DATASET="/home/surazz/projects/research_scripts/sampled_dataset_1_0_10minutes.csv"
OUTPUT_MAPPING="/home/surazz/projects/research_scripts/function_mapping.csv"

# Reversed Action List (map to HashFunctions dynamically)
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
    while IFS=, read -r -a row; do
        # Skip header
        if [[ "${row[0]}" == "HashOwner" || "${row[1]}" == "HashApp" || "${row[2]}" == "HashFunction" ]]; then
            continue
        fi

        # Extract HashFunction from the third column
        HASH_FUNCTION="${row[2]}"

        # Check the corresponding columns (minutes 1 to 10, columns 5 to 15)
        for i in {5..15}; do
            # Column index corresponds to minute number
            MINUTE=$((i - 4))
            if [[ "${row[$i]}" -eq 1 ]]; then
                # Find the corresponding action for the HashFunction
                FUNC="${hash_function_map[$HASH_FUNCTION]}"
                if [[ -n "$FUNC" ]]; then
                    echo "Invoking function: wsk -i action invoke $FUNC (Minute: $MINUTE)"
                    wsk -i action invoke "$FUNC" > /dev/null 2>&1
                    ((invocation_count++))  # Increment the counter
                fi
            fi
        done
    done < "$DATASET"
}

# Start invocation
echo "Starting function invocations based on the dataset..."
invoke_functions

# Output the total number of invocations
echo "Function invocation complete."
echo "Total number of invocations: $invocation_count"
