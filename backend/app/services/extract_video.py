from __future__ import annotations

from pathlib import Path

import cv2


def extract_frames(video_path: str, output_dir: str, every_n_seconds: int = 5) -> list[dict]:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frame_interval = int(fps * every_n_seconds)
    frames: list[dict] = []
    idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % frame_interval == 0:
            ts = idx / fps
            out_path = str(Path(output_dir) / f"frame_{idx}.jpg")
            cv2.imwrite(out_path, frame)
            frames.append({"timestamp": round(ts, 2), "path": out_path})
        idx += 1

    cap.release()
    return frames


def extract_poster(video_path: str, poster_path: str) -> bool:
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return False
    cv2.imwrite(poster_path, frame)
    return True
