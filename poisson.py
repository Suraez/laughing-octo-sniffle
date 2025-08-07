import asyncio
import aiohttp
import numpy as np
import re

# Step 1: Your trace (used as λ per second)
trace = [1, 2, 2, 8, 1, 3, 19, 7, 7, 10, 4, 5, 3, 3, 4, 21, 9, 12, 31, 6,
         3, 5, 2, 2, 2, 9, 3, 11, 7, 4, 5, 7, 3, 3, 4, 4, 10, 8, 2, 1,
         3, 1, 3, 4, 2, 3, 4, 11, 10, 4, 1, 3, 1, 2, 22, 19, 24, 31]

# Step 2: OpenFaaS function URL
FUNCTION_URL = "http://127.0.0.1:8080/function/graph-mst"

# Step 3: Storage for latencies
latencies = []

# Step 4: Async request sending with latency extraction
async def send_request(session, i, second):
    try:
        async with session.post(FUNCTION_URL) as resp:
            text = await resp.text()
            print(f"[Sec {second}] Req {i} - Status {resp.status} - Response: {text.strip()}")
            # Extract latency using regex
            match = re.search(r"Latency:\s*([\d.]+)", text)
            if match:
                latency_val = float(match.group(1))
                latencies.append(latency_val)
    except Exception as e:
        print(f"Request {i} failed at second {second}: {e}")

# Step 5: Main Poisson load generator
async def run_poisson_load():
    async with aiohttp.ClientSession() as session:
        i = 0
        for second, lam in enumerate(trace):
            n_requests = np.random.poisson(lam)
            print(f"Second {second}: Sending {n_requests} requests (λ={lam})")
            tasks = [send_request(session, i + j, second) for j in range(n_requests)]
            i += n_requests
            await asyncio.gather(*tasks)
            await asyncio.sleep(1)  # wait for next second

    # Step 6: After all done, calculate stats
    print("\n--- Summary ---")
    print(f"Total Requests: {len(latencies)}")
    
    if latencies:
        total_latency = sum(latencies)
        avg_latency = np.mean(latencies)
        min_latency = min(latencies)
        
        # Compute latency / min_latency (excluding the min itself)
        list_div = [lat / min_latency for lat in latencies if lat != min_latency]
        
        # Compute average of list_div
        avg_list_div = np.mean(list_div) if list_div else 0.0
        
        print(f"Total Latency (ms): {total_latency:.2f}")
        print(f"Average Latency (ms): {avg_latency:.2f}")
        print(f"Minimum Latency (ms): {min_latency:.2f}")
        print(f"Avg(latency / min_latency) [excluding min]: {avg_list_div:.4f}")
    else:
        print("No successful latencies recorded.")

# Step 7: Run it
asyncio.run(run_poisson_load())
