#!/bin/bash

NAMESPACE="openfaas-fn"
PYTHON_SCRIPT="per_pid_pages.py"

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

  # Call Python script to get memory stats
  sudo python3 "$PYTHON_SCRIPT" "$PID"
  echo ""
done
