# Frame Selection Runbook

## Purpose

Select labeling-ready frames from the 19,200-frame Round-1 raw set.

## Inputs

```text
task_A_dataset_frame/manifests/frames_raw_manifest.csv
task_A_dataset_frame/outputs/frames_raw/
```

## Command

```bash
.venv/bin/python task_A_dataset_frame/scripts/select_frames_for_labeling.py
```

## Method

The selection script uses:

1. proportional source quotas,
2. metadata-stratified coverage over episode/timeline,
3. lightweight image metrics: brightness, contrast, edge density, sharpness,
4. auto hard-case scoring.

## Outputs

```text
task_A_dataset_frame/outputs/frames_selected/600_baseline/
task_A_dataset_frame/outputs/frames_selected/cvat_batch_001/
task_A_dataset_frame/manifests/frames_selected_manifest.csv
task_A_dataset_frame/manifests/cvat_batch_001_manifest.csv
task_A_dataset_frame/manifests/hard_cases_manifest.csv
task_A_dataset_frame/outputs/archives/frames_selected_600_baseline.zip
task_A_dataset_frame/outputs/archives/cvat_batch_001_200.zip
task_A_dataset_frame/outputs/contact_sheets/
```

## Human Review Required

Auto scoring can suggest visual hardness but cannot reliably identify semantic cases such as objects near table edge, close objects, or occlusion before labels exist. Review the contact sheets and manually refine `hard_cases_manifest.csv` before final labeling/training decisions.

## Manual Deletion Audit

If bad/error frames are removed manually from selected folders, refresh manifests and archives so they match the remaining files. Current refreshed counts after manual audit:

```text
600_baseline: 583 retained / 17 removed
cvat_batch_001: 192 retained / 8 removed
hard_cases_manifest: 103 retained / 17 removed
```

Deletion audit logs:

```text
task_A_dataset_frame/logs/manual_deleted_frames_audit.csv
task_A_dataset_frame/logs/manual_deletion_summary.csv
```
