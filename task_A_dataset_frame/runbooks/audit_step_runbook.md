# Audit Step Runbook

## Purpose

Build a reliable inventory of `Part_Sorting` before extracting or selecting more frames.

## Step 1 - Confirm Source Dataset

Record:

- dataset root path
- dataset names
- episode count
- total frames
- fps
- available cameras
- video dimensions
- video codec

## Step 2 - Filter Source Files

For round 1, keep only:

```text
videos/observation.images.head_left/chunk-000/file-*.mp4
```

Exclude:

```text
head_right
wrist_left
wrist_right
```

## Step 3 - Validate Source Videos

For each filtered MP4, check:

- file exists
- file size > 0
- readable by video decoder
- fps is 30
- resolution is 640x480
- frame count is plausible
- duration is plausible

## Step 4 - Compare With Existing Extracted Frames

Compare source videos with existing frames under:

```text
data/derived/task1_detection/raw_frames/
```

Check:

- source dataset name
- camera
- file index
- frame index
- frame count
- duplicate filenames
- corrupt images

## Step 5 - Update Audit Report

Write conclusions to:

```text
reports/dataset_audit_report.md
```

Minimum final report sections:

1. Scope
2. Source dataset summary
3. Filtered `head_left` file list
4. Existing extracted-frame summary
5. Existing selected-frame summary
6. Metadata gaps
7. Blockers
8. Recommended next action
