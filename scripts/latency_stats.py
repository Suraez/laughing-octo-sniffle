import re
import numpy as np

LOG_FILE = "/home/suraj-desk/projects/laughing-octo-sniffle/scripts/activations_global_nov12.log"   # <-- Change your file name

# Run markers
run_start_re = re.compile(r"=== RUN (\d+) \[(fine_grained|global)\] START ===")


# Runtime detector: nodejs:12 / python:3.9
runtime_re = re.compile(r"\b(nodejs|python):")

# Warm/cold detection
warm_re = re.compile(r"\bwarm\b")
cold_re = re.compile(r"\bcold\b")

# Latency formats:
latency_ms_re = re.compile(r"\s+(\d+)ms\s+success")
latency_s_re  = re.compile(r"\s+([\d\.]+)s\s+success")


def percentile(data, p):
    return np.percentile(data, p) if data else None


def parse_log(filename):
    with open(filename, "r") as f:
        text = f.read()

    # Structure:
    # runs = {
    #   1: {
    #       "nodejs": { "latencies": [], "warm": 0, "cold": 0 },
    #       "python": { "latencies": [], "warm": 0, "cold": 0 }
    #   }
    # }
    runs = {}
    current_run = None

    for line in text.splitlines():

        # Detect new run block
        match_run = run_start_re.search(line)
        if match_run:
            current_run = int(match_run.group(1))
            runs[current_run] = {
                "nodejs": {"latencies": [], "warm": 0, "cold": 0},
                "python": {"latencies": [], "warm": 0, "cold": 0},
            }
            continue

        if current_run is None:
            continue

        # Identify runtime (nodejs or python)
        runtime_match = runtime_re.search(line)
        if not runtime_match:
            continue

        runtime = runtime_match.group(1)

        # Warm / Cold classification
        if warm_re.search(line):
            runs[current_run][runtime]["warm"] += 1
        elif cold_re.search(line):
            runs[current_run][runtime]["cold"] += 1

        # Extract latency "XXms"
        m_ms = latency_ms_re.search(line)
        if m_ms:
            latency_ms = int(m_ms.group(1))
            runs[current_run][runtime]["latencies"].append(latency_ms)
            continue

        # Extract latency "XX.Xs" and convert to ms
        m_s = latency_s_re.search(line)
        if m_s:
            latency_ms = float(m_s.group(1)) * 1000.0
            runs[current_run][runtime]["latencies"].append(latency_ms)
            continue

    return runs


def compute_stats(runs):
    print("\n=== Per-Run Benchmark Summary (latency in ms) ===\n")

    for run, benchmarks in runs.items():
        print(f"RUN {run}")

        for runtime in ["nodejs", "python"]:
            data = benchmarks[runtime]

            values = data["latencies"]
            warm_count = data["warm"]
            cold_count = data["cold"]

            if not values:
                print(f"  {runtime.capitalize()} Benchmark: no data\n")
                continue

            avg = np.mean(values)
            p95 = percentile(values, 95)
            p99 = percentile(values, 99)

            print(f"  {runtime.capitalize()} Benchmark:")
            print(f"    warm starts = {warm_count}")
            print(f"    cold starts = {cold_count}")
            print(f"    count       = {len(values)}")
            print(f"    avg         = {avg:.2f} ms")
            print(f"    p95         = {p95:.2f} ms")
            print(f"    p99         = {p99:.2f} ms\n")


if __name__ == "__main__":
    runs = parse_log(LOG_FILE)
    compute_stats(runs)
