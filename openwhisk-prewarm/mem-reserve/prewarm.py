import sys, time
mib = int(sys.argv[1]) if len(sys.argv) > 1 else 0
blocks = []
for _ in range(mib):
    b = bytearray(1024 * 1024)  # 1 MiB
    b[0] = 1
    blocks.append(b)
print(f"[prewarm] Holding {mib} MiB in RAM.", flush=True)
while True:
    time.sleep(3600)
