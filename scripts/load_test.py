import asyncio
import aiohttp
import time
import subprocess
from datetime import datetime
import argparse

URLS = {
    "dh": "http://172.17.0.1:3233/api/v1/web/guest/default/dh",
    "vp": "http://172.17.0.1:3233/api/v1/web/guest/default/vp"
}

REQUEST_TIMEOUT = 120  # seconds
LOG_FILE = "burst_requests_cli_poll.log"
POLL_INTERVAL = 5  
POLL_LIMIT = 8 


def log_line(text: str):
    """Print and write a timestamped line to the log file."""
    line = f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {text}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


async def poll_wsk(stop_event: asyncio.Event):
    """Poll wsk activation list periodically and log the last line."""
    log_line("Started OpenWhisk activation polling...")
    while not stop_event.is_set():
        try:
            cmd = ["wsk", "-i", "activation", "list", "--limit", str(POLL_LIMIT)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:
                    last_line = lines[1] if len(lines) > 1 else lines[0]
                    log_line(f"[ACTIVATION] {last_line}")
                else:
                    log_line("[ACTIVATION] No activations found.")
            else:
                log_line(f"[ACTIVATION ERROR] {result.stderr.strip()}")
        except Exception as e:
            log_line(f"[ACTIVATION EXCEPTION] {e}")
        await asyncio.sleep(POLL_INTERVAL)
    log_line("Stopped OpenWhisk activation polling.")


# --------------------------
# REQUEST HANDLER
# --------------------------
async def fire(session: aiohttp.ClientSession, url: str, label: str):
    """Send one request and record latency."""
    start = time.monotonic()
    try:
        async with session.get(url, ssl=False, timeout=REQUEST_TIMEOUT) as r:
            await r.read()
            latency = (time.monotonic() - start) * 1000  # ms
            status = r.status
            return (label, status, latency)
    except Exception as e:
        return (label, f"error:{e.__class__.__name__}", None)


# --------------------------
# MAIN BURST FUNCTION
# --------------------------
async def run_burst(vp_count: int, dh_count: int):
    total = vp_count + dh_count
    log_line(f"Starting burst of {total} concurrent requests ({vp_count}→vp, {dh_count}→dh)...")

    timeout = aiohttp.ClientTimeout(total=None, connect=REQUEST_TIMEOUT)
    connector = aiohttp.TCPConnector(ssl=False, limit=0)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = []
        for i in range(vp_count):
            tasks.append(asyncio.create_task(fire(session, URLS["vp"], f"vp-{i+1}")))
        for i in range(dh_count):
            tasks.append(asyncio.create_task(fire(session, URLS["dh"], f"dh-{i+1}")))

        start_wall = time.monotonic()
        results = await asyncio.gather(*tasks)
        wall_time = time.monotonic() - start_wall

    latencies = [r[2] for r in results if r[2] is not None]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    p95 = sorted(latencies)[int(0.95 * len(latencies))] if latencies else 0

    log_line(f"All requests completed in {wall_time:.2f}s")
    for label, status, latency in results:
        if latency:
            log_line(f"  {label:>6} | {status} | {latency:.2f} ms")
        else:
            log_line(f"  {label:>6} | {status} | failed")

    log_line(f"Summary: ok={len(latencies)} avg={avg_latency:.1f} ms p95={p95:.1f} ms")


# --------------------------
# ENTRY POINT
# --------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send concurrent bursts to vp/dh and poll OpenWhisk activations."
    )
    parser.add_argument("--vp", type=int, required=True, help="Number of concurrent requests for vp benchmark")
    parser.add_argument("--dh", type=int, required=True, help="Number of concurrent requests for dh benchmark")
    args = parser.parse_args()

    stop_event = asyncio.Event()

    async def orchestrator():
        # Run burst workload first
        await run_burst(vp_count=args.vp, dh_count=args.dh)

        # Optional delay before polling (to let activations register)
        delay_seconds = 5
        log_line(f"Waiting {delay_seconds}s before polling OpenWhisk activations...")
        await asyncio.sleep(delay_seconds)

        # Poll once after all requests finish
        log_line("Polling OpenWhisk activations after completion...")
        try:
            cmd = ["wsk", "-i", "activation", "list", "--limit", str(POLL_LIMIT)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                for line in lines[:10]:  # log first few lines for context
                    log_line(f"[ACTIVATION] {line}")
            else:
                log_line(f"[ACTIVATION ERROR] {result.stderr.strip()}")
        except Exception as e:
            log_line(f"[ACTIVATION EXCEPTION] {e}")


    asyncio.run(orchestrator())
