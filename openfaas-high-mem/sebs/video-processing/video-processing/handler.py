import subprocess
import os

def handle(event, context):
    base_dir = os.path.dirname(__file__)
    input_path = os.path.join(base_dir, "input.mp4")
    output_path = os.path.join(base_dir, "output.gif")
    watermark_path = os.path.join(base_dir, "watermark.png")

    # Accept raw binary data directly
    video_bytes = event.body

    with open(input_path, "wb") as f:
        f.write(video_bytes)

    print("DEBUG: received", len(video_bytes), "bytes")

    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, "-i", watermark_path,
            "-filter_complex", "overlay=10:10", "-t", "5",
            output_path
        ], check=True)

    except subprocess.CalledProcessError as e:
        return {
            "statusCode": 500,
            "body": f"FFmpeg processing failed: {str(e)}"
        }

    os.remove(input_path)
    os.remove(output_path)

    return {
        "statusCode": 200,
        "body": "added the watermark video"
    }
