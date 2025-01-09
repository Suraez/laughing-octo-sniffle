#!/bin/bash

# Generate a unique output file name with the current datetime
CURRENT_DATETIME=$(date +"%Y%m%d-%H-%M-%S")
OUTPUT_FILE="../memory-${CURRENT_DATETIME}.csv"

# Write the CSV header
echo "container_name,memory_usage,time" > $OUTPUT_FILE

# Function to capture CTRL-C and stop monitoring
trap "echo 'Stopping monitoring...'; exit" SIGINT

echo "Monitoring Docker containers. Output file: $OUTPUT_FILE"
echo "Press CTRL-C to stop."

# Declare an array to track seen containers
declare -A SEEN_CONTAINERS

# Monitor Docker ps continuously
while true; do
    # Get the list of currently active container IDs and names
    docker ps --format "{{.ID}},{{.Names}}" | while IFS=',' read -r CONTAINER_ID CONTAINER_NAME; do
        # If the container is new (not in SEEN_CONTAINERS), process it
        if [[ -z "${SEEN_CONTAINERS[$CONTAINER_ID]}" ]]; then
            SEEN_CONTAINERS["$CONTAINER_ID"]=1  # Mark this container as seen

            # Fetch the memory usage using docker stats for this container
            MEMORY_USAGE=$(docker stats --no-stream --format "{{.MemUsage}}" "$CONTAINER_ID")
            CURRENT_TIME=$(date +"%Y-%m-%d %I:%M:%S%p")

            # Log the container stats to the CSV file
            echo "$CONTAINER_NAME,$MEMORY_USAGE,$CURRENT_TIME" >> $OUTPUT_FILE
            echo "Logged: $CONTAINER_NAME,$MEMORY_USAGE,$CURRENT_TIME"
        fi
    done

    # Wait for a short interval before checking again
    sleep 1
done
