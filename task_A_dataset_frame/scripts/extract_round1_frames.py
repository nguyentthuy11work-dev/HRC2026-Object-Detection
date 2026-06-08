#!/usr/bin/env python3
"""Extract Round-1 short/head_left frames at 3 fps and create metadata manifest.

Run from repository root with the project virtualenv:

    .venv/bin/python task_A_dataset_frame/scripts/extract_round1_frames.py --clean

Requires `imageio-ffmpeg` installed in the active Python environment. The script
uses the bundled ffmpeg binary, extracts every 10th frame from 30 fps source
videos, renames frames with traceable metadata, and writes
`manifests/frames_raw_manifest.csv`.
"""

from __future__ import annotations

import argparse
import csv
import importlib
import shutil
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ROOT = REPO_ROOT / "task_A_dataset_frame"
SOURCE_MANIFEST = TASK_ROOT / "manifests" / "round1_short_head_left_sources.csv"
OUTPUT_DIR = TASK_ROOT / "outputs" / "frames_raw"
RAW_MANIFEST = TASK_ROOT / "manifests" / "frames_raw_manifest.csv"

SOURCE_FPS = 30
EXTRACT_FPS = 3
FRAME_STRIDE = SOURCE_FPS // EXTRACT_FPS
EPISODE_FRAMES = 192
WIDTH = 640
HEIGHT = 480


def clean_outputs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT_DIR.glob("*.jpg"):
        path.unlink()
    if RAW_MANIFEST.exists():
        RAW_MANIFEST.unlink()


def extract_temp_frames(ffmpeg: str, source_video: Path, temp_dir: Path) -> list[Path]:
    pattern = temp_dir / "frame_%06d.jpg"
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(source_video),
        "-vf",
        f"select='not(mod(n\\,{FRAME_STRIDE}))'",
        "-vsync",
        "vfr",
        "-q:v",
        "2",
        str(pattern),
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {source_video}:\n{proc.stderr[-3000:]}")
    return sorted(temp_dir.glob("frame_*.jpg"))


def parse_file_index(video_file: str) -> int:
    return int(video_file.replace("file-", "").replace(".mp4", ""))


def build_output_name(
    source_id: str,
    episode_index: int,
    source_frame_index: int,
    timestamp_ms: int,
) -> str:
    return (
        f"{source_id}_episode{episode_index:06d}_"
        f"frame{source_frame_index:06d}_t{timestamp_ms:06d}.jpg"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="remove existing raw JPGs and manifest first")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.clean:
        clean_outputs()

    imageio_ffmpeg = importlib.import_module("imageio_ffmpeg")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    rows: list[dict[str, object]] = []

    with SOURCE_MANIFEST.open(newline="") as handle:
        sources = list(csv.DictReader(handle))

    for source in sources:
        source_id = source["source_id"]
        source_video = Path(source["source_path"])
        episode_start = int(source["episode_start"])
        video_file = source["video_file"]
        file_index = parse_file_index(video_file)

        with tempfile.TemporaryDirectory(prefix=f"{source_id}_") as temp_name:
            temp_dir = Path(temp_name)
            temp_frames = extract_temp_frames(ffmpeg, source_video, temp_dir)

            expected_count = int(source["expected_extract_3fps_frames"])
            if len(temp_frames) != expected_count:
                raise RuntimeError(
                    f"Unexpected frame count for {source_id}: "
                    f"got {len(temp_frames)}, expected {expected_count}"
                )

            for selected_index, temp_frame in enumerate(temp_frames):
                source_frame_index = selected_index * FRAME_STRIDE
                episode_index = episode_start + source_frame_index // EPISODE_FRAMES
                episode_frame_index = source_frame_index % EPISODE_FRAMES
                timestamp_seconds = source_frame_index / SOURCE_FPS
                timestamp_ms = round(timestamp_seconds * 1000)
                output_name = build_output_name(
                    source_id, episode_index, source_frame_index, timestamp_ms
                )
                output_path = OUTPUT_DIR / output_name
                shutil.move(str(temp_frame), output_path)

                rows.append(
                    {
                        "frame_id": output_path.stem,
                        "dataset_split": "short",
                        "camera": "head_left",
                        "source_id": source_id,
                        "video_file": video_file,
                        "video_file_index": file_index,
                        "episode_index": episode_index,
                        "source_frame_index": source_frame_index,
                        "episode_frame_index": episode_frame_index,
                        "timestamp_seconds": f"{timestamp_seconds:.6f}",
                        "source_video": str(source_video),
                        "output_file": str(output_path.relative_to(REPO_ROOT)),
                        "width": WIDTH,
                        "height": HEIGHT,
                        "source_fps": SOURCE_FPS,
                        "extract_fps": EXTRACT_FPS,
                        "frame_stride": FRAME_STRIDE,
                    }
                )

    fieldnames = [
        "frame_id",
        "dataset_split",
        "camera",
        "source_id",
        "video_file",
        "video_file_index",
        "episode_index",
        "source_frame_index",
        "episode_frame_index",
        "timestamp_seconds",
        "source_video",
        "output_file",
        "width",
        "height",
        "source_fps",
        "extract_fps",
        "frame_stride",
    ]
    with RAW_MANIFEST.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Extracted {len(rows)} frames to {OUTPUT_DIR}")
    print(f"Wrote manifest to {RAW_MANIFEST}")


if __name__ == "__main__":
    main()
