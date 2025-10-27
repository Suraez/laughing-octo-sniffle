
# --------------------------
# this script accepts parameters i.e python load.py --vp 5 --dh 5
# --------------------------
import asyncio
import aiohttp
import time
from datetime import datetime
import argparse

# --------------------------
# CONFIGURATION
# --------------------------
URLS = {
    "dh": "http://172.17.0.1:3233/api/v1/web/guest/default/dh",
    "vp": "http://172.17.0.1:3233/api/v1/web/guest/default/vp"
}

REQUEST_TIMEOUT = 120  # seconds
LOG_FILE = "burst_requests_cli.log"


# --------------------------
# UTILITIES
# --------------------------
def log_line(text: str):
    """Print and write to log file."""
    line = f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {text}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# --------------------------
# CORE LOGIC
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


async def main(vp_count: int, dh_count: int):
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

    # Process results
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
        description="Send concurrent bursts of requests to vp and dh benchmarks."
    )
    parser.add_argument("--vp", type=int, required=True, help="Number of concurrent requests for vp benchmark")
    parser.add_argument("--dh", type=int, required=True, help="Number of concurrent requests for dh benchmark")

    args = parser.parse_args()
    asyncio.run(main(vp_count=args.vp, dh_count=args.dh))
