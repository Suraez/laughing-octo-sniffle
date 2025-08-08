import random
import time
import subprocess
from typing import List

def generate_inter_arrival_times(arrival_rate: int, duration: int) -> List[float]:
    inter_arrival_times = []
    time_elapsed = 0

    while time_elapsed < duration:
        inter_arrival_time = random.expovariate(arrival_rate)
        if time_elapsed + inter_arrival_time >= duration:
            break
        inter_arrival_times.append(inter_arrival_time)
        time_elapsed += inter_arrival_time

    return inter_arrival_times

arrival_rate = 1   # requests per second
duration = 30      # seconds
url = "https://192.168.49.2:31001/api/v1/web/guest/default/gp"

inter_arrival_times = generate_inter_arrival_times(arrival_rate, duration)

for i, inter_arrival_time in enumerate(inter_arrival_times):
    time.sleep(inter_arrival_time)

    print(f"[{i+1}] Sleeping {inter_arrival_time:.3f}s and sending request...")

    result = subprocess.run(["curl", "-k", url], capture_output=True, text=True)

    print(f"Response: {result.stdout.strip()}")
