import asyncio
import subprocess
import json
import time
from datetime import datetime
import requests
import os

# ----------------------------
# CONFIGURATION
# ----------------------------
URLS = {
    "dh": "http://172.17.0.1:3233/api/v1/web/guest/default/dh",
    "vp": "http://172.17.0.1:3233/api/v1/web/guest/default/vp",
    "ir": "http://172.17.0.1:3233/api/v1/web/guest/default/ir"
}

IR_ACTION = URLS["ir"]
DH_ACTION = URLS["dh"]
VERBOSE_LOGS = False  # Set True for detailed batch logs
LOG_TO_FILE = False

BATCH_SIZE_IR = 4
BATCH_SIZE_DH = 4
EXPERIMENT_DURATION = 180   # seconds (3 minutes)

# ----------------------------
# LOGGING SETUP
# ----------------------------
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = f"experiment_log_nomem_{TIMESTAMP}.log"
ACTIVATION_LOG = f"activations_global_{datetime.now().strftime('%b%d').lower()}.log"

def log(msg, also_print=True):
    ts = time.strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    if also_print:
        print(line)
    if LOG_TO_FILE:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")


# ----------------------------
# UTILITIES
# ----------------------------
def invoke_action_sync(action_url: str, batch_num: int, index: int):
    """Invoke a web action via HTTP POST; only log errors or exceptions."""
    start = time.monotonic()
    try:
        response = requests.post(action_url, timeout=120)
        latency = (time.monotonic() - start) * 1000

        # Log only if request failed
        if response.status_code != 200:
            log(f"[ERROR] {action_url} batch={batch_num} idx={index} code={response.status_code} latency={latency:.2f}ms")
            return ("error", latency)

        # Don't log successful responses to keep logs clean
        return ("ok", latency)

    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        log(f"[EXCEPTION] {action_url} batch={batch_num} idx={index} latency={latency:.2f}ms err={e}")
        return ("error", latency)


async def run_ir_batch(batch_num):
    """Run one IR batch asynchronously (4 concurrent invocations)."""
    if VERBOSE_LOGS:
        log(f"Starting IR batch #{batch_num} with {BATCH_SIZE_IR} requests...")
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, invoke_action_sync, IR_ACTION, batch_num, i + 1)
        for i in range(BATCH_SIZE_IR)
    ]
    results = await asyncio.gather(*tasks)
    latencies = [lat for _, lat in results if lat > 0]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    if VERBOSE_LOGS:
        log(f"IR batch #{batch_num} completed. avg latency = {avg_latency:.1f} ms")
    return results


def run_dh_batch(batch_num):
    """Run one DH batch synchronously (4 sequential invocations)."""
    if VERBOSE_LOGS:
        log(f"Starting DH batch #{batch_num} with {BATCH_SIZE_DH} requests...")
    results = []
    for i in range(BATCH_SIZE_DH):
        status, latency = invoke_action_sync(DH_ACTION, batch_num, i + 1)
        results.append((status, latency))
    avg_latency = sum(lat for _, lat in results if lat > 0) / len(results)
    if VERBOSE_LOGS:
        log(f"DH batch #{batch_num} completed. avg latency = {avg_latency:.1f} ms")
    return results


def fetch_all_activations_final():
    """Fetch all activations after experiment completion using pagination."""
    log("Fetching all activations (final, paginated)...")
    limit = 200
    skip = 0
    tmp_file = f"/tmp/activations_tmp_{int(time.time())}.log"
    total = 0
    first_batch = True

    with open(tmp_file, "w") as tmp:
        while True:
            cmd = ["wsk", "-i", "activation", "list", "--limit", str(limit), "--skip", str(skip)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            lines = result.stdout.strip().split("\n")
            if len(lines) <= 1:
                break
            total += len(lines) - 1

            if first_batch:
                tmp.write("\n".join(lines) + "\n")
                first_batch = False
            else:
                tmp.write("\n".join(lines[1:]) + "\n")
            skip += limit

    log(f"Fetched {total} activation entries, sorting and filtering...")

    # Sort chronologically by timestamp
    sorted_lines = subprocess.run(["sort", "-k1,2", tmp_file],
                                  capture_output=True, text=True).stdout.splitlines()

    # Filter out first 8 cold starts
    filtered_lines = []
    cold_seen = 0
    for line in sorted_lines:
        if "cold" in line and cold_seen < 8:
            cold_seen += 1
            continue
        filtered_lines.append(line)

    with open(ACTIVATION_LOG, "a") as outf:
        outf.write("\n".join(filtered_lines) + "\n")

    os.remove(tmp_file)
    log(f"All activations saved to {ACTIVATION_LOG} ({len(filtered_lines)} entries)")


# ----------------------------
# MAIN EXPERIMENT LOGIC
# ----------------------------
async def orchestrate():
    log("=== EXPERIMENT START (no memory.high) ===")
    log(f"Duration: {EXPERIMENT_DURATION/60:.1f} min | Log: {LOG_FILE}")
    start_time = time.monotonic()
    dh_batches = 0
    ir_batches = 0

    while True:
        if time.monotonic() - start_time >= EXPERIMENT_DURATION:
            break
        ir_batches += 1
        ir_task = asyncio.create_task(run_ir_batch(ir_batches))
        while not ir_task.done() and (time.monotonic() - start_time) < EXPERIMENT_DURATION:
            dh_batches += 1
            run_dh_batch(dh_batches)
            await asyncio.sleep(0.5)
        await ir_task
        await asyncio.sleep(1)

    fetch_all_activations_final()

    log("=== EXPERIMENT COMPLETE ===")
    log(f"Total IR batches: {ir_batches}")
    log(f"Total DH batches: {dh_batches}")
    log("=== END ===")


if __name__ == "__main__":
    asyncio.run(orchestrate())
