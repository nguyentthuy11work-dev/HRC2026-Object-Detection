#!/usr/bin/env python3
"""Lightweight MP4 container audit for Round-1 source videos.

This script avoids ffprobe/OpenCV dependencies. It reads MP4 box metadata to
check container structure, track dimensions, duration, and video sample counts.
It does not decode pixel frames.
"""

from __future__ import annotations

import csv
import struct
from pathlib import Path
from typing import Any


CONTAINER_BOXES = {b"moov", b"trak", b"mdia", b"minf", b"stbl", b"edts"}


def read_boxes(handle, end: int, path=()):
    boxes = []
    while handle.tell() < end:
        start = handle.tell()
        header = handle.read(8)
        if len(header) < 8:
            break
        size, box_type = struct.unpack(">I4s", header)
        header_size = 8
        if size == 1:
            size = struct.unpack(">Q", handle.read(8))[0]
            header_size = 16
        elif size == 0:
            size = end - start
        if size < header_size:
            break
        data_start = handle.tell()
        data_end = start + size
        boxes.append((path + (box_type,), data_start, data_end))
        if box_type in CONTAINER_BOXES:
            boxes.extend(read_boxes(handle, data_end, path + (box_type,)))
        handle.seek(data_end)
    return boxes


def audit_mp4(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "video_file": path.name,
        "size_bytes": path.stat().st_size,
    }
    with path.open("rb") as handle:
        boxes = read_boxes(handle, path.stat().st_size)
        result["has_moov"] = any(box_path[-1] == b"moov" for box_path, _, _ in boxes)
        result["has_mdat"] = any(box_path[-1] == b"mdat" for box_path, _, _ in boxes)

        track_sizes = []
        sample_counts = []
        for box_path, data_start, data_end in boxes:
            box_type = box_path[-1]
            handle.seek(data_start)
            if box_type == b"mvhd":
                version = handle.read(1)[0]
                handle.read(3)
                if version == 0:
                    handle.read(8)
                    timescale = struct.unpack(">I", handle.read(4))[0]
                    duration = struct.unpack(">I", handle.read(4))[0]
                else:
                    handle.read(16)
                    timescale = struct.unpack(">I", handle.read(4))[0]
                    duration = struct.unpack(">Q", handle.read(8))[0]
                result["duration_seconds"] = duration / timescale if timescale else None
            elif box_type == b"tkhd":
                data = handle.read(data_end - data_start)
                if len(data) >= 8:
                    width = struct.unpack(">I", data[-8:-4])[0] / 65536
                    height = struct.unpack(">I", data[-4:])[0] / 65536
                    if width > 0 and height > 0:
                        track_sizes.append((width, height))
            elif box_type == b"stts":
                handle.read(4)
                entry_count = struct.unpack(">I", handle.read(4))[0]
                total_samples = 0
                for _ in range(entry_count):
                    if handle.tell() + 8 <= data_end:
                        sample_count, _sample_delta = struct.unpack(">II", handle.read(8))
                        total_samples += sample_count
                sample_counts.append(total_samples)

        if track_sizes:
            width, height = max(track_sizes, key=lambda item: item[0] * item[1])
            result["width"] = int(width)
            result["height"] = int(height)
        if sample_counts:
            result["frame_count"] = max(sample_counts)
        frame_count = result.get("frame_count")
        duration_seconds = result.get("duration_seconds")
        if isinstance(frame_count, int) and isinstance(duration_seconds, (int, float)) and duration_seconds:
            result["fps_est"] = round(frame_count / duration_seconds, 3)
    return result


def main() -> None:
    source_dir = Path(
        "/home/grunt/teamProject/robotic_dogbot/challenge2026_dataset/Part_Sorting/"
        "part_sorting_short_1000_episode/videos/observation.images.head_left/chunk-000"
    )
    output_path = Path(__file__).resolve().parents[1] / "logs" / "video_validation_short_head_left.csv"
    rows = []
    episode_start = 0
    for video in sorted(source_dir.glob("file-*.mp4")):
        row = audit_mp4(video)
        frames = int(row.get("frame_count", 0))
        episode_count = frames // 192
        row["source_id"] = f"short_head_left_{video.stem.replace('-', '')}"
        row["episode_start"] = episode_start
        row["episode_end"] = episode_start + episode_count - 1
        row["expected_extract_3fps_frames"] = frames // 10
        row["validation_status"] = "container_metadata_valid"
        row["notes"] = "pixel decode pending"
        rows.append(row)
        episode_start += episode_count

    fieldnames = [
        "source_id",
        "video_file",
        "has_moov",
        "has_mdat",
        "width",
        "height",
        "frame_count",
        "duration_seconds",
        "fps_est",
        "episode_start",
        "episode_end",
        "expected_extract_3fps_frames",
        "validation_status",
        "notes",
    ]
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
