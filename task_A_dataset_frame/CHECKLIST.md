# Task A Checklist

## 1. Dataset Audit

- [x] Locate raw `Part_Sorting` dataset.
- [x] Identify dataset format: LeRobot v3.0.
- [x] Identify available splits: `part_sorting_short_1000_episode`, `part_sorting_long_756_episode`.
- [x] Identify available cameras: `head_left`, `head_right`, `wrist_left`, `wrist_right`.
- [x] Confirm round-1 camera scope: `head_left` only.
- [x] Confirm round-1 dataset split: `part_sorting_short_1000_episode` only.
- [x] Verify every Round-1 `head_left` video has valid MP4 container metadata.
- [x] Verify frame count/duration for every Round-1 `head_left` video from MP4 metadata.
- [x] Map Round-1 video files to episode ranges.
- [x] Pixel-decode sample frames from each Round-1 video using bundled ffmpeg.
- [x] Finalize current `dataset_audit_report.md` for Round-1 extraction readiness.

## 2. File Filtering

- [x] Define round-1 filter: keep only `videos/observation.images.head_left/**/file-*.mp4`.
- [x] Count `head_left` files: short = 4 mp4, long = 10 mp4.
- [x] Create candidate filtered source list: `manifests/source_head_left_files.csv`.
- [x] Decide whether round-1 uses `short` only or `short + long`: **short only**.
- [x] Produce a final filtered source list for extraction: `manifests/round1_short_head_left_sources.csv`.

## 3. Frame Extraction

- [x] Existing extracted raw frames found: 5,856 JPG frames.
- [x] Confirm existing 5,856-frame subset matches expected 3 fps extraction from `short/head_left/file-000.mp4`.
- [x] Confirm existing frames source is very likely `short/head_left/file-000`, based on filename and exact frame-count match.
- [x] Confirm expected Round-1 extraction count: 19,200 frames at 3 fps from 192,000 source frames.
- [x] Extract full Round-1 `head_left` frames into `outputs/frames_raw/`.
- [x] Record `episode`, `camera`, `video_file`, frame indices, and timestamp in `manifests/frames_raw_manifest.csv`.

## 4. Frame Selection

- [x] Existing 600-frame candidate set found.
- [x] Existing candidate zip found.
- [x] Existing manifest found.
- [x] Auto-select new 600-frame baseline from the 19,200-frame Round-1 raw set.
- [x] Create CVAT batch 001 with 200 frames.
- [x] Manual-audit selected images and remove obvious bad/error frames.
- [x] Refresh manifests, archives, and contact sheets after manual deletion audit.
- [x] Validate selected source paths exist.
- [x] Remove duplicates if any.
- [x] Check selected-frame timeline coverage.
- [x] Create current `manifests/frames_selected_manifest.csv` with retained frames.
- [x] Create current `manifests/cvat_batch_001_manifest.csv` with retained frames.
- [x] Create CVAT-ready zip archives.
- [x] Create contact sheets for quick visual review.
- [ ] Backfill 17 baseline frames if the final deliverable must remain exactly 600.
- [ ] Backfill 8 CVAT batch frames if batch 001 must remain exactly 200.
- [ ] Human-review refreshed contact sheets for semantic diversity: object rotation, object proximity, table-edge cases, clutter, occlusion.

## 5. Hard Cases + LocateAnything

- [x] Create initial auto-scored `manifests/hard_cases_manifest.csv`.
- [x] Define initial auto hard-case tags: `motion_blur_candidate`, `poor_lighting_candidate`, `clutter_candidate`, `visual_hard_candidate`.
- [x] Remove hard-case candidates corresponding to manually deleted baseline frames.
- [ ] Human-review hard cases and add semantic tags: `clutter`, `occlusion`, `near_edge`, `close_objects`, `motion_blur`, `poor_lighting`, `detection_failure`.
- [ ] Run LocateAnything on sample hard frames.
- [ ] Use LocateAnything output only to prioritize labeling, not as ground truth.
