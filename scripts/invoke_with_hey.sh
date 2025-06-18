#!/bin/bash

# Usage:
# ./invoke_with_hey.sh --bert 100 --chamelon 100 --matmul 20 --duration 2m

# Default values
BERT_QPS=0
CHAMELON_QPS=0
MATMUL_QPS=0
DURATION="1m"  # Default duration

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --bert) BERT_QPS="$2"; shift ;;
        --chamelon) CHAMELON_QPS="$2"; shift ;;
        --matmul) MATMUL_QPS="$2"; shift ;;
        --duration) DURATION="$2"; shift ;;
        *) echo "❌ Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Function to run hey with rate limit
run_hey() {
    local NAME=$1
    local URL=$2
    local DATA=$3
    local QPS=$4
    local DURATION=$5

    if [ "$QPS" -gt 0 ]; then
        echo "▶️ Invoking $NAME at $QPS RPS for $DURATION"
        if [ -z "$DATA" ]; then
            hey -z "$DURATION" -q "$QPS" -c 5 "$URL"
        else
            hey -z "$DURATION" -q "$QPS" -c 5 -m POST -d "$DATA" "$URL"
        fi
        echo "✅ Done with $NAME"
        echo
    fi
}

# Run each configured test
run_hey "bert"     "http://127.0.0.1:8080/function/bert"     "the capital of france is" "$BERT_QPS" "$DURATION"
run_hey "chamelon" "http://127.0.0.1:8080/function/chamelon" ""                         "$CHAMELON_QPS" "$DURATION"
run_hey "matmul"   "http://127.0.0.1:8080/function/matmul"   "1000"                     "$MATMUL_QPS" "$DURATION"
