import asyncio
import aiohttp
import time
import subprocess
from datetime import datetime
import argparse
import re

URLS = {
    "dh": "http://172.17.0.1:3233/api/v1/web/guest/default/dh",
    "vp": "http://172.17.0.1:3233/api/v1/web/guest/default/vp"
}

REQUEST_TIMEOUT = 120
LOG_FILE = "burst_requests_cli_poll_31_v3.log"

# --------------------------
# CONFIGURE ROUNDS HERE
# -------------------------- 
ROUNDS = [
    {"vp": 5, "dh": 4},
    {"vp": 5, "dh": 3},
    {"vp": 4, "dh": 4},
    {"vp": 5, "dh": 2},
    {"vp": 3, "dh": 4},
]

def log_line(text: str):
    """Print and write a timestamped line to the log file."""
    line = f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {text}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# --------------------------
# ACTIVATION UTILITIES
# --------------------------
def parse_activation_id(line: str):
    """Extract Activation ID (first 32-hex token)."""
    m = re.search(r"\b([0-9a-f]{32})\b", line)
    return m.group(1) if m else None

def classify_start_field(line: str):
    """Detect 'cold' or 'warm' from the Start column."""
    if re.search(r"\bcold\b", line, re.IGNORECASE):
        return "cold"
    if re.search(r"\bwarm\b", line, re.IGNORECASE):
        return "warm"
    return None

def log_activations_with_delta(prev_ids: set, limit: int):
    """
    Logs recent activations and counts new cold/warm starts.
    Returns (new_lines, new_ids, counts)
    """
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

    # Skip header
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
    """Send one request and record latency."""
    start = time.monotonic()
    try:
        async with session.get(url, ssl=False, timeout=REQUEST_TIMEOUT) as r:
            await r.read()
            latency = (time.monotonic() - start) * 1000
            return (label, r.status, latency)
    except Exception as e:
        return (label, f"error:{e.__class__.__name__}", None)

# --------------------------
# RUN ONE BURST ROUND
# --------------------------
async def run_burst(vp_count: int, dh_count: int, round_num: int, prev_ids: set):
    total = vp_count + dh_count
    poll_limit = total  # dynamic: poll as many activations as requests we sent this round

    log_line(f"\n--- ROUND {round_num} START ---")
    log_line(f"Starting burst of {total} concurrent requests ({vp_count}→vp, {dh_count}→dh)...")

    timeout = aiohttp.ClientTimeout(total=None, connect=REQUEST_TIMEOUT)
    connector = aiohttp.TCPConnector(ssl=False, limit=0)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = [asyncio.create_task(fire(session, URLS["vp"], f"vp-{i+1}")) for i in range(vp_count)]
        tasks += [asyncio.create_task(fire(session, URLS["dh"], f"dh-{i+1}")) for i in range(dh_count)]

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

    # wait before polling activations
    await asyncio.sleep(5)
    log_line(f"Polling OpenWhisk activations after Round {round_num} with limit={poll_limit}...")
    new_lines, new_ids, counts = log_activations_with_delta(prev_ids, limit=poll_limit)

    cold_count = counts.get("cold", 0)
    warm_count = counts.get("warm", 0)
    log_line(f"Round {round_num}: Cold starts detected = {cold_count} (warm={warm_count})")
    log_line(f"--- ROUND {round_num} END ---\n")

    return {"round": round_num, "vp": vp_count, "dh": dh_count, "cold": cold_count, "warm": warm_count, "p95": p95}, new_ids

# --------------------------
# MAIN ORCHESTRATOR
# --------------------------
async def orchestrator():
    all_rounds = []
    total_cold_excl_first = 0
    first_round_cold = 0
    prev_ids = set()

    # initial snapshot: seed with the max round size
    initial_limit = max((cfg["vp"] + cfg["dh"]) for cfg in ROUNDS)

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
        result, new_ids = await run_burst(config["vp"], config["dh"], i, prev_ids)
        all_rounds.append(result)
        if i == 1:
            first_round_cold = result["cold"]
        else:
            total_cold_excl_first += result["cold"]
        prev_ids |= new_ids
        await asyncio.sleep(10)  # delay between rounds

    log_line("=== ALL ROUNDS COMPLETE ===")
    for r in all_rounds:
        log_line(f"Round {r['round']}: vp={r['vp']} dh={r['dh']} p95={r['p95']:.1f}ms cold={r['cold']} warm={r['warm']}")

    # show "A - B = C" where A is total including first, B is first round cold, C excludes first
    grand_total_incl_first = first_round_cold + total_cold_excl_first
    log_line(f"Total cold starts across all rounds: {grand_total_incl_first}-{first_round_cold} = {total_cold_excl_first}")

# --------------------------
# ENTRY POINT
# --------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send multi-round bursts to vp/dh.")
    args = parser.parse_args()
    asyncio.run(orchestrator())
