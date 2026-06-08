# Dataset Audit Report

Status: Round-1 audit and raw-frame extraction complete.

## Scope

- Dataset: `Part_Sorting`
- Round-1 split: `part_sorting_short_1000_episode` only
- Round-1 camera: `head_left`
- Target extraction fps: 3 fps

## Known Source Summary

| Dataset | Episodes | Frames | FPS | Notes |
|---|---:|---:|---:|---|
| `part_sorting_short_1000_episode` | 1000 | 192,000 | 30 | short sequence |
| `part_sorting_long_756_episode` | 756 | 580,608 | 30 | deferred for later round |

## Round-1 Filtered Sources

Round 1 uses only these 4 source videos:

```text
part_sorting_short_1000_episode/videos/observation.images.head_left/chunk-000/file-000.mp4
part_sorting_short_1000_episode/videos/observation.images.head_left/chunk-000/file-001.mp4
part_sorting_short_1000_episode/videos/observation.images.head_left/chunk-000/file-002.mp4
part_sorting_short_1000_episode/videos/observation.images.head_left/chunk-000/file-003.mp4
```

Basic file existence/size audit:

| Source | Exists | Size | Frames | Duration | FPS | Resolution | Episode range | 3 fps frames |
|---|---:|---:|---:|---:|---:|---|---|---:|
| `file-000.mp4` | yes | 200.69 MiB | 58,560 | 1952.0 s | 30.0 | 640x480 | 0-304 | 5,856 |
| `file-001.mp4` | yes | 200.48 MiB | 58,560 | 1952.0 s | 30.0 | 640x480 | 305-609 | 5,856 |
| `file-002.mp4` | yes | 200.27 MiB | 58,560 | 1952.0 s | 30.0 | 640x480 | 610-914 | 5,856 |
| `file-003.mp4` | yes | 55.86 MiB | 16,320 | 544.0 s | 30.0 | 640x480 | 915-999 | 1,632 |

Container metadata validation confirms `moov` and `mdat` boxes, dimensions, duration, FPS estimate, and frame/sample count. Pixel-decode validation was completed by extracting one sample JPEG from each video using the bundled ffmpeg binary from `imageio-ffmpeg`.

Expected total Round-1 extraction at 3 fps:

```text
19,200 frames
```

## Known Existing Outputs

| Item | Path | Count |
|---|---|---:|
| Raw frames | `data/derived/task1_detection/raw_frames/` | 5,856 JPG |
| Selected frames | `data/derived/task1_detection/label_candidates/head_left_file000_600/` | 600 JPG |
| Selected manifest | `data/derived/task1_detection/label_candidates/manifest.csv` | 600 rows + header |

## New Round-1 Extraction Outputs

| Item | Path | Count |
|---|---|---:|
| Raw frames | `task_A_dataset_frame/outputs/frames_raw/` | 19,200 JPG |
| Raw manifest | `task_A_dataset_frame/manifests/frames_raw_manifest.csv` | 19,200 rows + header |
| Extraction script | `task_A_dataset_frame/scripts/extract_round1_frames.py` | 1 |
| Decode samples | `task_A_dataset_frame/logs/video_decode_samples/` | 4 JPG |

Extraction distribution:

| Source | Extracted frames |
|---|---:|
| `short_head_left_file000` | 5,856 |
| `short_head_left_file001` | 5,856 |
| `short_head_left_file002` | 5,856 |
| `short_head_left_file003` | 1,632 |

Verification summary:

```text
jpg_count = 19,200
manifest_rows = 19,200
duplicate_frame_ids = 0
missing_output_files = 0
episode range = 0-999
```

## Current Gaps

- Existing selected manifest lacks `episode`, `camera`, `video_file`, `frame_index`, and `timestamp_seconds` columns.
- Existing 5,856 old-path raw frames are treated as legacy output. The new Round-1 raw frame set supersedes them.
- Frame selection and hard-case filtering still need to be performed from the new 19,200-frame raw set.

## Next Audit Action

Backfill manually deleted frames if exact 600/200 counts are required, review refreshed contact sheets, upload the current CVAT archive to CVAT for initial labeling, and manually refine `hard_cases_manifest.csv` tags.

## New Frame Selection Outputs

Selection was automated with `task_A_dataset_frame/scripts/select_frames_for_labeling.py` using metadata-stratified sampling plus image metrics (`brightness`, `contrast`, `edge_density`, `sharpness`, `hard_score`).

| Item | Path | Count |
|---|---|---:|
| Baseline frames retained after manual audit | `task_A_dataset_frame/outputs/frames_selected/600_baseline/` | 583 JPG |
| CVAT batch 001 frames retained after manual audit | `task_A_dataset_frame/outputs/frames_selected/cvat_batch_001/` | 192 JPG |
| Selected manifest | `task_A_dataset_frame/manifests/frames_selected_manifest.csv` | 583 rows + header |
| CVAT batch manifest | `task_A_dataset_frame/manifests/cvat_batch_001_manifest.csv` | 192 rows + header |
| Hard-case candidates | `task_A_dataset_frame/manifests/hard_cases_manifest.csv` | 103 rows + header |
| Baseline archive | `task_A_dataset_frame/outputs/archives/frames_selected_600_baseline.zip` | 583 JPG |
| CVAT archive | `task_A_dataset_frame/outputs/archives/cvat_batch_001_200.zip` | 192 JPG |

Original auto-selected 600-frame baseline distribution before manual deletion:

| Source | Frames |
|---|---:|
| `file-000.mp4` | 183 |
| `file-001.mp4` | 183 |
| `file-002.mp4` | 183 |
| `file-003.mp4` | 51 |

Original auto-selected 200-frame CVAT batch distribution before manual deletion:

| Source | Frames |
|---|---:|
| `file-000.mp4` | 61 |
| `file-001.mp4` | 61 |
| `file-002.mp4` | 61 |
| `file-003.mp4` | 17 |

Contact sheets for manual review:

```text
task_A_dataset_frame/outputs/contact_sheets/baseline_600_contact_sheet.jpg
task_A_dataset_frame/outputs/contact_sheets/cvat_batch_001_contact_sheet.jpg
task_A_dataset_frame/outputs/contact_sheets/hard_case_candidates_contact_sheet.jpg
```

## Manual Deletion Audit

After visual audit, bad/error frames were manually removed from the selected folders. The manifests, archives, contact sheets, and hard-case candidate list were refreshed to match the remaining files.

| Set | Removed | Retained |
|---|---:|---:|
| `600_baseline` | 17 | 583 |
| `cvat_batch_001` | 8 | 192 |
| `hard_cases_manifest` | 17 | 103 |

Logs:

```text
task_A_dataset_frame/logs/manual_deleted_frames_audit.csv
task_A_dataset_frame/logs/manual_deletion_summary.csv
```

If the deliverable must be exactly 600 baseline frames and exactly 200 initial CVAT frames, backfill is still required.
