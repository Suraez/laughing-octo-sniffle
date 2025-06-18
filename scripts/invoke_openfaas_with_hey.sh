#!/bin/bash

# Usage example:
# ./invoke_with_hey.sh --bert 50 --chamelon 30 --matmul 20 --timeout 10

# Default values
BERT=0
CHAMELON=0
MATMUL=0
TIMEOUT=10  # Timeout per request in seconds

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --bert) BERT="$2"; shift ;;
        --chamelon) CHAMELON="$2"; shift ;;
        --matmul) MATMUL="$2"; shift ;;
        --timeout) TIMEOUT="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Function to run hey for a given function
run_hey() {
    local NAME=$1
    local URL=$2
    local DATA=$3
    local COUNT=$4
    local TIMEOUT=$5

    if [ "$COUNT" -gt 0 ]; then
        echo "▶️ Invoking $NAME $COUNT times with timeout $TIMEOUT sec each"
        if [ -z "$DATA" ]; then
            hey -n "$COUNT" -c 5 -t "$TIMEOUT" "$URL"
        else
            hey -n "$COUNT" -c 5 -t "$TIMEOUT" -m POST -d "$DATA" "$URL"
        fi
        echo "✅ Done with $NAME"
        echo
    fi
}

# Run hey for each function
run_hey "bert"     "http://127.0.0.1:8080/function/bert"     "the capital of france is" "$BERT" "$TIMEOUT"
run_hey "chamelon" "http://127.0.0.1:8080/function/chamelon" ""                         "$CHAMELON" "$TIMEOUT"
run_hey "matmul"   "http://127.0.0.1:8080/function/matmul"   "1000"                     "$MATMUL" "$TIMEOUT"
