import subprocess
import os

def handle(event, context):
    # Use files that are baked into the image
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "input.mp4")
    watermark_path = os.path.join(base_dir, "watermark.png")
    output_path = os.path.join("/tmp", "output.gif")  # write to a safe temp directory

    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, "-i", watermark_path,
            "-filter_complex", "overlay=10:10", "-t", "5",
            output_path
        ], check=True)

        # Optionally, return something meaningful
        return {
            "statusCode": 200,
            "body": "Successfully added watermark to video."
        }

    except subprocess.CalledProcessError as e:
        return {
            "statusCode": 500,
            "body": f"FFmpeg processing failed: {str(e)}"
        }
