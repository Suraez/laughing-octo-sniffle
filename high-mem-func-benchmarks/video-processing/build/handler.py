import cv2
import numpy as np

def handler(event, context):
    cap = cv2.VideoCapture("sample_video.mp4")
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(np.array(frame))
    cap.release()
    # Simulate heavy memory use
    processed_frames = [frame ** 2 for frame in frames]
    return {"status": "Success", "num_frames_processed": len(processed_frames)}
