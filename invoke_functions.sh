#!/bin/bash

#Things to do:
#1. correct the mapping of the hash functions

# Input file
DATASET="/home/surazz/projects/research_scripts/sampled_dataset_0_1_10minutes.csv"
OUTPUT_MAPPING="/home/surazz/projects/research_scripts/function_mapping.csv"

# HashFunction mapping (replace with dynamic fetch if needed)
declare -A HASH_FUNCTIONS=(
    [1]="dg"
    [2]="ds"
    [3]="dq"
    [4]="dl"
    [5]="dt"
    [6]="gp"
    [7]="gm"
    [8]="gb"
    [9]="md"
    [10]="dv"
)

# Output the mapping to CSV
echo "Column,HashFunction,FunctionName" > "$OUTPUT_MAPPING"
for i in "${!HASH_FUNCTIONS[@]}"; do
    echo "$i,HashFunction${i},${HASH_FUNCTIONS[$i]}" >> "$OUTPUT_MAPPING"
done

echo "Mapping saved to $OUTPUT_MAPPING."

# # Function to invoke actions based on the dataset
# invoke_functions() {
#     while IFS=, read -r -a row; do
#         # Skip header
#         if [[ "${row[0]}" == "Column_Header_Name" ]]; then
#             continue
#         fi

#         # Columns 5 to 15 represent 1 to 10
#         for i in {5..15}; do
#             if [[ "${row[$i]}" -eq 1 ]]; then
#                 FUNC=${HASH_FUNCTIONS[$((i-4))]}  # Adjust column index to hash function mapping
#                 echo "Invoking function: wsk -i action invoke $FUNC"
#                 wsk -i action invoke "$FUNC" > /dev/null 2>&1
#             fi
#         done
#     done < "$DATASET"
# }

invoke_functions() {
    while IFS=, read -r -a row; do
        # Skip header
        if [[ "${row[0]}" == "Column_Header_Name" ]]; then
            continue
        fi

        # Columns 5 to 15 represent 1 to 10
        for i in {5..15}; do
            if [[ "${row[$i]}" -eq 1 ]]; then
                FUNC=${HASH_FUNCTIONS[$((i-4))]}  # Adjust column index to hash function mapping
                echo "Invoking function: wsk -i action invoke $FUNC"
                wsk -i action invoke "$FUNC" > /dev/null 2>&1 &
                sleep 0.1
            fi
        done

        # Wait for all parallel invocations in the current second to complete
        wait
    done < "$DATASET"
}


# Start invocation
echo "Starting function invocations based on the dataset..."
invoke_functions
echo "Function invocation complete."

