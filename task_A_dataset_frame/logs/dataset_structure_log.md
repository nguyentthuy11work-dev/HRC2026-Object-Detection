# Dataset Structure Log

Audit date: 2026-06-08

## Source Dataset

```text
/home/grunt/teamProject/robotic_dogbot/challenge2026_dataset/Part_Sorting
```

## Top-Level Structure

```text
Part_Sorting/
├── episodes.jsonl
├── tasks.jsonl
├── part_sorting_short_1000_episode/
└── part_sorting_long_756_episode/
```

## Dataset Summary

| Dataset | Episodes | Total frames | FPS | Frames/episode | Approx duration/episode |
|---|---:|---:|---:|---:|---:|
| `part_sorting_short_1000_episode` | 1000 | 192,000 | 30 | 192 | 6.4 s |
| `part_sorting_long_756_episode` | 756 | 580,608 | 30 | 768 | 25.6 s |
| **Total** | **1,756** | **772,608** | **30** | - | - |

## Data Format

- Format: LeRobot v3.0
- Robot type: `walker_s2_sim`
- Video path template: `videos/{video_key}/chunk-{chunk_index:03d}/file-{file_index:03d}.mp4`
- Data path template: `data/chunk-{chunk_index:03d}/file-{file_index:03d}.parquet`
- Image size: 640 x 480
- Channels: 3
- Codec: H.264
- Pixel format: `yuv420p`
- Audio: none

## Available Cameras

```text
observation.images.head_left
observation.images.head_right
observation.images.wrist_left
observation.images.wrist_right
```

## Video File Counts by Camera

### `part_sorting_short_1000_episode`

| Camera | MP4 files | File range |
|---|---:|---|
| `head_left` | 4 | `file-000.mp4` - `file-003.mp4` |
| `head_right` | 4 | `file-000.mp4` - `file-003.mp4` |
| `wrist_left` | 4 | `file-000.mp4` - `file-003.mp4` |
| `wrist_right` | 3 | `file-000.mp4` - `file-002.mp4` |

### `part_sorting_long_756_episode`

| Camera | MP4 files | File range |
|---|---:|---|
| `head_left` | 10 | `file-000.mp4` - `file-009.mp4` |
| `head_right` | 10 | `file-000.mp4` - `file-009.mp4` |
| `wrist_left` | 11 | `file-000.mp4` - `file-010.mp4` |
| `wrist_right` | 7 | `file-000.mp4` - `file-006.mp4` |

## Size Summary

| Dataset | Size |
|---|---:|
| `part_sorting_short_1000_episode` | 2.4G |
| `part_sorting_long_756_episode` | 7.3G |
| **Part_Sorting total** | **9.6G** |

## Notes

- LeRobot v3 stores multiple episodes inside each MP4 file; MP4 file count is not equal to episode count.
- `Part_Sorting/episodes.jsonl` at the top level is empty; episode metadata appears under each dataset's `meta/episodes/chunk-000/file-000.parquet`.
- `ffprobe`, `cv2`, and `pyarrow` are not available in the current environment, so deeper video/parquet validation requires installing tools or using another environment.
- Round-1 short/head_left MP4 container metadata was validated with a pure-Python MP4 parser. This confirms container structure, dimensions, duration, and sample counts, but not pixel decoding.

## Round-1 Episode Ranges From MP4 Metadata

Short episodes have 192 frames each. MP4 sample counts map to episode ranges as follows:

| Source | Frame count | Duration | Episode range | Expected 3 fps frames |
|---|---:|---:|---|---:|
| `file-000.mp4` | 58,560 | 1952.0 s | 0-304 | 5,856 |
| `file-001.mp4` | 58,560 | 1952.0 s | 305-609 | 5,856 |
| `file-002.mp4` | 58,560 | 1952.0 s | 610-914 | 5,856 |
| `file-003.mp4` | 16,320 | 544.0 s | 915-999 | 1,632 |

Total Round-1 source frames: 192,000. Expected Round-1 extraction at 3 fps: 19,200 frames.
