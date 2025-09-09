import time
import json
import subprocess
import os

def handler(event, context=None):
    start = time.time()

    # Optional: accept dynamic file names from event (if needed in future)
    try:
        data = json.loads(event.get("body", "{}"))
        duration = str(data.get("duration", 5))
    except Exception:
        duration = "5"

    # Static file paths (assumed to be packaged in image)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "input.mp4")
    watermark_path = os.path.join(base_dir, "watermark.png")
    output_path = os.path.join("/tmp", "output.gif")

    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, "-i", watermark_path,
            "-filter_complex", "overlay=10:10", "-t", duration,
            output_path
        ], check=True)

        latency = time.time() - start

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Watermarking successful.",
                "latency": latency,
                "output_path": output_path
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }

    except subprocess.CalledProcessError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": f"FFmpeg failed: {str(e)}"
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }


if __name__ == "__main__":
    print(handler({"body": "{}"}))
