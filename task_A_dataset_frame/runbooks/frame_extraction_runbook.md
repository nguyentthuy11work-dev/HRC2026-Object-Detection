# Frame Extraction Runbook

Status: draft. Use after audit validation is complete.

## Target

Extract `head_left` frames at 3 fps from `part_sorting_short_1000_episode` videos.

## Tooling

System `ffmpeg` was unavailable, so Round-1 extraction uses the bundled ffmpeg
binary from the repository virtual environment package `imageio-ffmpeg`.

Setup:

```bash
python -m venv .venv
.venv/bin/python -m pip install imageio-ffmpeg
```

Run extraction:

```bash
.venv/bin/python task_A_dataset_frame/scripts/extract_round1_frames.py --clean
```

Expected output after successful Round-1 extraction:

```text
task_A_dataset_frame/outputs/frames_raw/               # 19,200 JPG
task_A_dataset_frame/manifests/frames_raw_manifest.csv # 19,200 rows + header
```

## Output Location

```text
task_A_dataset_frame/outputs/frames_raw/
```

## Round-1 Source Manifest

Use:

```text
task_A_dataset_frame/manifests/round1_short_head_left_sources.csv
```

## Naming Convention

Recommended filename:

```text
{dataset_split}_head_left_file{video_file_index}_episode{episode_index}_frame{frame_index}_t{timestamp_ms}.jpg
```

Example:

```text
short_head_left_file000_episode000123_frame000090_t003000.jpg
```

## Required Metadata

Each extracted frame should be tracked with:

```text
dataset_split,camera,source_id,video_file,episode_index,source_frame_index,episode_frame_index,timestamp_seconds,source_video,output_file
```

## FPS Logic

Source videos are 30 fps. Extracting 3 fps means keeping every 10th source frame.

```text
keep_frame = frame_index % 10 == 0
timestamp_seconds = frame_index / 30.0
```

## Notes

- Do not use LocateAnything to generate labels.
- LocateAnything can be used later to identify hard frames for labeling priority.
