# File Filtering Log

## Round-1 Filter Rule

Only include `head_left` videos from the short split for the first object-detection baseline.

```text
Part_Sorting/part_sorting_short_1000_episode/videos/observation.images.head_left/chunk-000/file-*.mp4
```

Deferred for later rounds:

```text
Part_Sorting/part_sorting_long_756_episode/**
Part_Sorting/*/videos/observation.images.head_right/**
Part_Sorting/*/videos/observation.images.wrist_left/**
Part_Sorting/*/videos/observation.images.wrist_right/**
```

## Round-1 Selected Source Files

### Short Dataset

```text
challenge2026_dataset/Part_Sorting/part_sorting_short_1000_episode/videos/observation.images.head_left/chunk-000/file-000.mp4
challenge2026_dataset/Part_Sorting/part_sorting_short_1000_episode/videos/observation.images.head_left/chunk-000/file-001.mp4
challenge2026_dataset/Part_Sorting/part_sorting_short_1000_episode/videos/observation.images.head_left/chunk-000/file-002.mp4
challenge2026_dataset/Part_Sorting/part_sorting_short_1000_episode/videos/observation.images.head_left/chunk-000/file-003.mp4
```

## Deferred Source Files

The long split is not used in Round 1. Keep it for future expansion after the short/head_left pipeline is stable.

### Long Dataset `head_left` Files

```text
challenge2026_dataset/Part_Sorting/part_sorting_long_756_episode/videos/observation.images.head_left/chunk-000/file-000.mp4
challenge2026_dataset/Part_Sorting/part_sorting_long_756_episode/videos/observation.images.head_left/chunk-000/file-001.mp4
challenge2026_dataset/Part_Sorting/part_sorting_long_756_episode/videos/observation.images.head_left/chunk-000/file-002.mp4
challenge2026_dataset/Part_Sorting/part_sorting_long_756_episode/videos/observation.images.head_left/chunk-000/file-003.mp4
challenge2026_dataset/Part_Sorting/part_sorting_long_756_episode/videos/observation.images.head_left/chunk-000/file-004.mp4
challenge2026_dataset/Part_Sorting/part_sorting_long_756_episode/videos/observation.images.head_left/chunk-000/file-005.mp4
challenge2026_dataset/Part_Sorting/part_sorting_long_756_episode/videos/observation.images.head_left/chunk-000/file-006.mp4
challenge2026_dataset/Part_Sorting/part_sorting_long_756_episode/videos/observation.images.head_left/chunk-000/file-007.mp4
challenge2026_dataset/Part_Sorting/part_sorting_long_756_episode/videos/observation.images.head_left/chunk-000/file-008.mp4
challenge2026_dataset/Part_Sorting/part_sorting_long_756_episode/videos/observation.images.head_left/chunk-000/file-009.mp4
```

## Expected 3 FPS Extraction Volume for Round 1

Original dataset FPS is 30. Extracting at 3 fps means approximately 1 frame every 10 original frames.

| Dataset | Original frames | Approx frames at 3 fps | Round-1 status |
|---|---:|---:|---|
| short | 192,000 | 19,200 | selected |
| long | 580,608 | 58,061 | deferred |
| short + long | 772,608 | 77,261 | not used in Round 1 |

## Current Derived Frame Status

Existing old-path raw frames:

```text
data/derived/task1_detection/raw_frames/ # 5,856 JPG frames
```

Existing old-path selected frames:

```text
data/derived/task1_detection/label_candidates/head_left_file000_600/ # 600 JPG frames
```

Interpretation: existing extracted frames likely cover only `part_sorting_short_1000_episode/head_left/file-000.mp4`. MP4 metadata shows `file-000.mp4` has 58,560 source frames, which yields exactly 5,856 frames at 3 fps. This matches the existing old-path raw frame count of 5,856.

## Closed Decisions

- [x] Round-1 extraction covers `short` only.

## Open Decisions

- [ ] Should existing 5,856 frames be migrated/copied into `task_A_dataset_frame/outputs/frames_raw/` or left as legacy derived data?
- [ ] Should the 600-frame baseline be rebuilt after full audit, or should the existing 600 set be used as the first labeling batch?
