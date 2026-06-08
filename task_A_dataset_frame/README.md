# Task A - Dataset + Frame Preparation

## Objective

Prepare a clean frame dataset for manual labeling and baseline object-detection training from the `Part_Sorting` dataset.

## Round-1 Scope

- Dataset: `Part_Sorting`
- Dataset split: `part_sorting_short_1000_episode` only
- Camera: `observation.images.head_left` only
- Source dataset path: `/home/grunt/teamProject/robotic_dogbot/challenge2026_dataset/Part_Sorting`
- Frame extraction target: 3 fps
- Baseline manual labeling target: 600 diverse frames

## Workspace Layout

```text
task_A_dataset_frame/
├── README.md
├── CHECKLIST.md
├── logs/
│   ├── dataset_structure_log.md
│   └── file_filtering_log.md
├── reports/
│   └── dataset_audit_report.md
├── runbooks/
│   ├── audit_step_runbook.md
│   └── frame_extraction_runbook.md
├── manifests/
│   ├── source_head_left_files.csv
│   ├── round1_short_head_left_sources.csv
│   ├── frames_selected_manifest.csv
│   └── hard_cases_manifest.csv
└── outputs/
    ├── frames_raw/
    └── frames_selected/
        └── 600_baseline/
```

## Existing Derived Data Found

Existing extracted/selected frames currently live under the old `data/` path:

```text
data/derived/task1_detection/raw_frames/                         # 5,856 JPG frames
data/derived/task1_detection/label_candidates/head_left_file000_600/ # 600 JPG frames
data/derived/task1_detection/label_candidates/manifest.csv       # 600 selected rows + header
```

Future outputs for this task should be written under:

```text
task_A_dataset_frame/outputs/
```

## Current Round-1 Labeling Outputs

```text
task_A_dataset_frame/outputs/frames_selected/600_baseline/       # 583 retained frames after manual audit
task_A_dataset_frame/outputs/frames_selected/cvat_batch_001/     # 192 retained frames after manual audit
task_A_dataset_frame/outputs/archives/cvat_batch_001_200.zip     # upload-ready current CVAT batch
task_A_dataset_frame/outputs/contact_sheets/                     # review sheets
task_A_dataset_frame/manifests/frames_selected_manifest.csv
task_A_dataset_frame/manifests/cvat_batch_001_manifest.csv
task_A_dataset_frame/manifests/hard_cases_manifest.csv
task_A_dataset_frame/logs/manual_deleted_frames_audit.csv
task_A_dataset_frame/logs/manual_deletion_summary.csv
```
