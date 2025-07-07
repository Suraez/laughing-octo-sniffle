# ./memory-stress-anon/handler.py
import json
import time

def handle(event, context):
    start = time.time()

    # Allocate and modify a large list (anonymous memory)
    data = [0] * 10_000_000  # ~80 MB
    for i in range(0, len(data), 256):
        data[i] = i % 256  # write to touch pages

    elapsed = time.time() - start
    return json.dumps({"elapsed_time_sec": elapsed})
