#!/bin/bash

NAMESPACE="openfaas-fn"
PYTHON_SCRIPT="per_pid_pages.py"
CSV_FILE="function_memory_stats.csv"
TIMESTAMP=$(date +%s)  # ← UNIX epoch time

# Create CSV header if file doesn't exist
if [ ! -f "$CSV_FILE" ]; then
    echo "timestamp,pod_name,pid,process_name,anonymous_pages,file_backed_pages,memory_consumption_mb,memory_pressure_percent" >> "$CSV_FILE"
fi

# Get system-wide memory usage (in MB)
MEM_TOTAL_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
MEM_AVAILABLE_KB=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
MEM_PRESSURE=$(echo "scale=4; (1 - $MEM_AVAILABLE_KB / $MEM_TOTAL_KB) * 100" | bc)

echo "Fetching pods in namespace '$NAMESPACE'..."
PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers | awk '{print $1}')

for POD in $PODS; do
  echo "🔍 Processing pod: $POD"

  # Get container ID
  CONTAINER_ID=$(sudo crictl ps -o json | jq -r --arg POD "$POD" '
    .containers[] | select(.labels."io.kubernetes.pod.name" == $POD) | .id')

  if [ -z "$CONTAINER_ID" ]; then
    echo "  ❌ Could not find container ID for pod $POD"
    continue
  fi

  # Get PID
  PID=$(sudo crictl inspect "$CONTAINER_ID" | jq -r '.info.pid')

  if [ -z "$PID" ] || [ "$PID" = "0" ]; then
    echo "  ❌ Could not find valid PID for container $CONTAINER_ID"
    continue
  fi

  echo "  ✅ PID for pod $POD: $PID"

  # Run Python script and capture output
  OUTPUT=$(sudo python3 "$PYTHON_SCRIPT" "$PID")

  # Extract values from output
  PROCESS_NAME=$(echo "$OUTPUT" | grep "Process:" | awk '{print $2}')

  ANON_PAGES=$(echo "$OUTPUT" | grep "Anonymous pages" | cut -d ':' -f 2 | awk '{print $1}')
  FILE_PAGES=$(echo "$OUTPUT" | grep "File-backed pages" | cut -d ':' -f 2 | awk '{print $1}')


  if [ -z "$ANON_PAGES" ] || [ -z "$FILE_PAGES" ]; then
    echo "  ⚠️ Skipping pod $POD due to missing memory data"
    continue
  fi

  # Calculate function memory in MB
  TOTAL_PAGES=$((ANON_PAGES + FILE_PAGES))
  FUNC_MEM_MB=$(echo "scale=2; $TOTAL_PAGES * 4 / 1024" | bc)

  # Append to CSV
  echo "$TIMESTAMP,$POD,$PID,$PROCESS_NAME,$ANON_PAGES,$FILE_PAGES,$FUNC_MEM_MB,$MEM_PRESSURE" >> "$CSV_FILE"

done
