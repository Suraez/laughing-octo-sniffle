import asyncio
import random
import time
from typing import Optional

import aiohttp

# --------------------------
# Config
# --------------------------
arrival_rate = 2    # requests per second (pick something realistic for one host)
duration = 10         # seconds to generate requests
url = "https://192.168.49.2:31001/api/v1/web/guest/default/ir"

# Execution controls
concurrency_limit = 2000        # max in-flight requests at once (protects your box)
request_timeout_s = 5           # per-request timeout
grace_period_s = 3              # after generation ends, how long to wait for stragglers
print_every = 1000              # progress print cadence (set None to disable)

# --------------------------
# Implementation
# --------------------------

class Stats:
    __slots__ = ("sent", "ok", "err")
    def __init__(self):
        self.sent = 0
        self.ok = 0
        self.err = 0

async def fire(session: aiohttp.ClientSession, url: str, sem: asyncio.Semaphore,
               stats: Stats) -> None:
    # Bound concurrency so latency spikes don’t explode memory
    async with sem:
        try:
            # Disable TLS verification (equivalent to curl -k)
            # and apply a client-side timeout.
            async with session.get(url, ssl=False, timeout=request_timeout_s) as r:
                await r.read()  # drain the body; avoid per-request printing
                if 200 <= r.status < 400:
                    stats.ok += 1
                else:
                    stats.err += 1
        except Exception:
            stats.err += 1

async def main():
    stats = Stats()
    sem = asyncio.Semaphore(concurrency_limit)
    tasks = set()

    # Use a single session for connection reuse
    timeout = aiohttp.ClientTimeout(total=None, connect=request_timeout_s)
    connector = aiohttp.TCPConnector(ssl=False, limit=0)  # limit=0 -> unlimited sockets (concurrency still bounded by sem)

    start = time.monotonic()
    end = start + duration
    next_send_at = start

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        while True:
            # Draw next interarrival and compute absolute send time
            inter = random.expovariate(arrival_rate)
            next_send_at += inter
            if next_send_at >= end:
                break

            # Sleep until the scheduled absolute time (no drift accumulation)
            now = time.monotonic()
            if next_send_at > now:
                await asyncio.sleep(next_send_at - now)

            # Fire concurrently (don't await here)
            t = asyncio.create_task(fire(session, url, sem, stats))
            tasks.add(t)
            stats.sent += 1

            # Periodically prune finished tasks and print progress
            if len(tasks) % 2048 == 0:
                tasks = {t for t in tasks if not t.done()}
            if print_every and stats.sent % print_every == 0:
                elapsed = time.monotonic() - start
                print(f"Sent {stats.sent} in {elapsed:.2f}s | ok={stats.ok} err={stats.err} inflight={len(tasks)}")

        # Optional: allow in-flight requests a short grace period to finish
        if tasks:
            try:
                await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True),
                                       timeout=grace_period_s)
            except asyncio.TimeoutError:
                for t in tasks:
                    t.cancel()
                # Give cancellations a brief moment
                with contextlib.suppress(Exception):
                    await asyncio.gather(*tasks, return_exceptions=True)

    wall = time.monotonic() - start
    print(f"\nDone. Wall time: {wall:.2f}s "
          f"| generated_for≈{duration}s | sent={stats.sent} ok={stats.ok} err={stats.err}")

if __name__ == "__main__":
    import contextlib
    asyncio.run(main())
