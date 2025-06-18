#!/bin/bash

BASE_DIR="/home/suraj-desk/projects/laughing-octo-sniffle/openfaas-high-mem" # Change this to your base directory

echo "Searching for stack.yml files under $BASE_DIR..."

find "$BASE_DIR" -type f -name "stack.yaml" | while read -r stack_file; do
  echo "Found: $stack_file"
  dir=$(dirname "$stack_file")
  echo "Deploying from $dir"
  (cd "$dir" && faas-cli up -f stack.yaml)
done
