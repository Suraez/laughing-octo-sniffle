from flask import Flask, Response
import subprocess
import re

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World"

@app.route("/metrics")
def metrics():
    try:
        result = subprocess.run(
            ["wsk", "-i", "activation", "list", "--limit", "50"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        durations = []

        for line in result.stdout.splitlines():
            if "Duration" in line:
                continue
            match = re.search(r'\s+(\d+\.?\d*)ms', line)
            if match:
                duration = float(match.group(1))
                durations.append(duration)

        avg_latency = sum(durations) / len(durations) if durations else 0.0

        output = [
            "# HELP openwhisk_avg_latency_ms Average activation latency in milliseconds",
            "# TYPE openwhisk_avg_latency_ms gauge",
            f"openwhisk_avg_latency_ms {avg_latency}"
        ]
        return Response("\n".join(output), mimetype="text/plain")

    except Exception as e:
        return Response(f"# ERROR: {e}", mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
