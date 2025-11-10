import asyncio
import aiohttp
import time
import subprocess
from datetime import datetime
import argparse
import re
import os

# --------------------------
# CONSTANTS
# --------------------------
BASE_URL = "http://172.17.0.1:3233/api/v1/web/guest/default"
REQUEST_TIMEOUT = 120

# --------------------------
# CLI ARGUMENTS
# --------------------------
parser = argparse.ArgumentParser(description="Send multi-round bursts to two workloads.")
parser.add_argument("--w1", default="ir", help="First workload name (default: ir)")
parser.add_argument("--w2", default="dh", help="Second workload name (default: dh)")
parser.add_argument("--mem-high", type=int, default=104857600,
                    help="Value (in bytes) to set for memory.high for dh containers after each round (default: 100MB)")
parser.add_argument("--cgroup-parent", type=str, default="docker_elastic.slice",
                    help="Parent slice name under /sys/fs/cgroup (default: docker_elastic.slice)")
parser.add_argument("--round-delay", type=int, default=10,
                    help="Seconds to wait between rounds (default: 10s)")
args = parser.parse_args()

# --------------------------
# DYNAMIC CONFIG
# --------------------------
URLS = {
    args.w1: f"{BASE_URL}/{args.w1}",
    args.w2: f"{BASE_URL}/{args.w2}"
}
LOG_FILE = f"burst_requests_{args.w1}_{args.w2}_{datetime.now().strftime('%b%d').lower()}.log"

# Configure rounds (you can modify as needed)
ROUNDS = [
    {"w1": 4, "w2": 4},
    {"w1": 4, "w2": 4},
    {"w1": 4, "w2": 4},
    {"w1": 4, "w2": 4},
    {"w1": 4, "w2": 4}
]

# --------------------------
# LOGGING
# --------------------------
def log_line(text: str):
    line = f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {text}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# --------------------------
# ACTIVATION UTILITIES
# --------------------------
def parse_activation_id(line: str):
    m = re.search(r"\b([0-9a-f]{32})\b", line)
    return m.group(1) if m else None

def classify_start_field(line: str):
    if re.search(r"\bcold\b", line, re.IGNORECASE):
        return "cold"
    if re.search(r"\bwarm\b", line, re.IGNORECASE):
        return "warm"
    return None

def log_activations_with_delta(prev_ids: set, limit: int):
    cmd = ["wsk", "-i", "activation", "list", "--limit", str(limit)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log_line(f"[ACTIVATION ERROR] {result.stderr.strip()}")
        return [], set(), {"cold": 0, "warm": 0}

    lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
    if not lines:
        log_line("[ACTIVATION] No activations found.")
        return [], set(), {"cold": 0, "warm": 0}

    for l in lines:
        log_line(f"[ACTIVATION] {l}")

    body = lines[1:] if lines and lines[0].lower().startswith("datetime") else lines
    new_lines, new_ids = [], set()
    counts = {"cold": 0, "warm": 0}

    for l in body:
        act_id = parse_activation_id(l)
        if not act_id:
            continue
        if act_id not in prev_ids:
            new_ids.add(act_id)
            new_lines.append(l)
            cls = classify_start_field(l)
            if cls in counts:
                counts[cls] += 1

    return new_lines, new_ids, counts

# --------------------------
# REQUEST HANDLER
# --------------------------
async def fire(session: aiohttp.ClientSession, url: str, label: str):
    start = time.monotonic()
    try:
        async with session.get(url, ssl=False, timeout=REQUEST_TIMEOUT) as r:
            await r.read()
            latency = (time.monotonic() - start) * 1000
            return (label, r.status, latency)
    except Exception as e:
        return (label, f"error:{e.__class__.__name__}", None)

# --------------------------
# MEMORY HIGH UTILITY
# --------------------------
def set_memory_high_for_dh(mem_high: int, cgroup_parent: str):
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=_dh", "-q"],
            capture_output=True, text=True
        )
        ids = [cid.strip() for cid in result.stdout.splitlines() if cid.strip()]
        if not ids:
            log_line("No _dh containers found.")
            return

        for cid in ids:
            inspect = subprocess.run(
                ["docker", "inspect", "--format", "{{.Id}}", cid],
                capture_output=True, text=True
            )
            full_id = inspect.stdout.strip()
            scope = f"/sys/fs/cgroup/{cgroup_parent}/docker-{full_id}.scope"
            if not os.path.exists(scope):
                log_line(f"[WARN] Scope not found: {scope}")
                continue

            log_line(f"Setting memory.high={mem_high} for container {cid} ...")
            try:
                subprocess.run(
                    ["sudo", "tee", os.path.join(scope, "memory.high")],
                    input=str(mem_high).encode(),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                log_line(f"[ERROR] Failed for {cid}: {e}")
    except Exception as e:
        log_line(f"[EXCEPTION] set_memory_high_for_dh: {e}")

# --------------------------
# RUN ONE BURST ROUND
# --------------------------
async def run_burst(w1_name: str, w2_name: str, w1_count: int, w2_count: int, round_num: int, prev_ids: set):
    total = w1_count + w2_count
    poll_limit = total

    log_line(f"\n--- ROUND {round_num} START ---")
    log_line(f"Starting burst of {total} concurrent requests ({w1_count}→{w1_name}, {w2_count}→{w2_name})...")

    timeout = aiohttp.ClientTimeout(total=None, connect=REQUEST_TIMEOUT)
    connector = aiohttp.TCPConnector(ssl=False, limit=0)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = [asyncio.create_task(fire(session, URLS[w1_name], f"{w1_name}-{i+1}")) for i in range(w1_count)]
        tasks += [asyncio.create_task(fire(session, URLS[w2_name], f"{w2_name}-{i+1}")) for i in range(w2_count)]

        start_wall = time.monotonic()
        results = await asyncio.gather(*tasks)
        wall_time = time.monotonic() - start_wall

    latencies = [r[2] for r in results if r[2] is not None]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    p95 = sorted(latencies)[int(0.95 * len(latencies))] if latencies else 0

    log_line(f"All requests completed in {wall_time:.2f}s")
    for label, status, latency in results:
        log_line(f"  {label:>6} | {status} | {latency:.2f} ms" if latency else f"  {label:>6} | {status} | failed")

    log_line(f"Round {round_num} Summary: ok={len(latencies)} avg={avg_latency:.1f} ms p95={p95:.1f} ms")

    await asyncio.sleep(5)
    log_line(f"Polling OpenWhisk activations after Round {round_num} with limit={poll_limit}...")
    new_lines, new_ids, counts = log_activations_with_delta(prev_ids, limit=poll_limit)

    cold_count = counts.get("cold", 0)
    warm_count = counts.get("warm", 0)
    log_line(f"Round {round_num}: Cold starts detected = {cold_count} (warm={warm_count})")
    log_line(f"--- ROUND {round_num} END ---\n")

    return {"round": round_num, w1_name: w1_count, w2_name: w2_count,
            "cold": cold_count, "warm": warm_count, "p95": p95}, new_ids

# --------------------------
# MAIN ORCHESTRATOR
# --------------------------
async def orchestrator(mem_high: int, cgroup_parent: str, round_delay: int):
    all_rounds = []
    total_cold_excl_first = 0
    first_round_cold = 0
    prev_ids = set()

    initial_limit = max((cfg["w1"] + cfg["w2"]) for cfg in ROUNDS)
    initial_lines = subprocess.run(
        ["wsk", "-i", "activation", "list", "--limit", str(initial_limit)],
        capture_output=True, text=True
    )
    if initial_lines.returncode == 0:
        for l in initial_lines.stdout.strip().split("\n"):
            act_id = parse_activation_id(l)
            if act_id:
                prev_ids.add(act_id)

    for i, config in enumerate(ROUNDS, start=1):
        result, new_ids = await run_burst(args.w1, args.w2, config["w1"], config["w2"], i, prev_ids)
        all_rounds.append(result)

        if i == 1:
            first_round_cold = result["cold"]
        else:
            total_cold_excl_first += result["cold"]

        prev_ids |= new_ids

        if mem_high is not None:
            set_memory_high_for_dh(mem_high, cgroup_parent)

        await asyncio.sleep(round_delay)

    log_line("=== ALL ROUNDS COMPLETE ===")
    for r in all_rounds:
        log_line(f"Round {r['round']}: {args.w1}={r[args.w1]} {args.w2}={r[args.w2]} "
                 f"p95={r['p95']:.1f}ms cold={r['cold']} warm={r['warm']}")

    grand_total_incl_first = first_round_cold + total_cold_excl_first
    log_line(f"Total cold starts across all rounds: "
             f"{grand_total_incl_first}-{first_round_cold} = {total_cold_excl_first}")

# --------------------------
# ENTRY POINT
# --------------------------
if __name__ == "__main__":
    asyncio.run(orchestrator(args.mem_high, args.cgroup_parent, args.round_delay))
