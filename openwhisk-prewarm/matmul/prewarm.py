import time
import numpy as np

# Hardcode n to ~4 GiB total for A, B, C (float64), with some headroom
n = 13200

# Keep strong references so memory remains allocated after matmul
A = np.random.rand(n, n)
B = np.random.rand(n, n)

t0 = time.time()
C = A @ B
latency = time.time() - t0

# Report and hold
total_bytes = (A.nbytes + B.nbytes + C.nbytes)
print(f"[prewarm] n={n}, matmul latency={latency:.3f}s, holding ~{total_bytes/1024**3:.2f} GiB in RAM.", flush=True)

# Keep the process alive so memory stays resident
while True:
    time.sleep(3600)