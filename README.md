# Gait Analysis - Study 1 segmentation

This repository contains force-myography (FMG) band recordings and left/right
insole recordings from 8 healthy participants and 2 participants with
amputation. The pipeline segments the supplied Study 1 dataset into
trigger-delimited walking trials and heel-strike-to-heel-strike gait cycles,
then resamples each eight-channel FMG cycle to 101 points (0-100% of a cycle).

## Study 1 goal

The supplied brief proposes a seven-class assistive-device control problem:

1. gait initiation;
2. gait termination;
3. steady normal-step walking;
4. steady short-step walking;
5. steady long-step walking;
6. short-to-long transition; and
7. long-to-short transition.

The PDF lists condition counts but does **not** include the trial-to-condition
protocol. Therefore this project does not guess normal/short/long/transition
labels. The first and last complete cycles in a trial are labelled
`gait_initiation` and `gait_termination`; interior cycles are conservatively
labelled `unassigned_steady_or_transition`. A protocol sheet is required before
training a scientifically valid seven-class model.

## Dataset layout

Each canonical block has three synchronized files:

- `X_1` / `X_21`: time, trigger, 8 left FMG and 8 right FMG channels;
- `X_1L` / `X_21L`: time, trigger, CoP, left vGRF;
- `X_1R` / `X_21R`: time, trigger, CoP, right vGRF.

The number suffix is the first trial represented by that triplet. Some subjects
use aggregate blocks (`1`, `21`, and sometimes `30`), while `Sub06_H` and
`Sub07_H` contain individual-trial triplets. The next available suffix bounds an
aggregate block, avoiding overlap. The nested `Sub04_H/Sub04_H` directory,
optional underscore before `L/R`, and `.txt` suffix are handled automatically.

## Segmentation method

1. Read only complete 18-column FMG and 4-column insole rows, safely skipping
   the truncated first line found in several exports.
2. Convert contiguous high trigger pulses into marker regions. Consecutive
   marker pairs delimit a walking trial.
3. Smooth vGRF with a 70 ms rolling median and derive hysteresis thresholds
   from its 10th and 90th percentiles.
4. Detect contacts with a 400 ms refractory period and require unloading within
   2 seconds. Both signal polarities are evaluated because one supplied insole
   channel is inverted; the plausible result closest to 11 contacts is used.
5. Map contacts to FMG using elapsed time from trial start; the devices use
   different sampling rates.
6. Cut each side's eight FMG channels between contacts and resample to 101
   points.
7. Mark trials outside the broad 6-16 cycles-per-side range as `CHECK`.

Raw files are never modified.

## Run

```bash
python3 -m pip install -r requirements.txt
python3 run_study1.py
python3 plot_study1.py
python3 create_desired_segmentation.py
```

## Outputs

Results are written to `output/study1/`:

- `dataset_inventory.csv` - source triplets and totals per subject/block;
- `trial_summary.csv` - trial sample/contact/cycle counts and QA status;
- `cycle_metadata.csv` - one row per cycle with source indices, duration, side,
  boundary label, and adaptive threshold;
- `cycles_normalized_101.csv` - model-ready `cycle_id`, cycle percentage, and
  eight FMG channels.
- `plots/*_normalized_fmg_qa.png` - subject/side mean +/- one standard deviation
  for normalized FMG channel 1;
- `plots/all_subject_cycle_counts.png` - segmented-cycle counts by subject/side.
- `cycle_phase_labels.csv` - cycle-level GI, SSSW/SSLW, SLT/LST, and GT labels;
- `phase_summary.csv` - inferred transition direction, boundary, duration change,
  and confidence for each trial/side;
- `annotated_trials/*.png` - final annotated plots with eight FMG channels, CoP,
  vGRF, and dashed phase boundaries in the style of the supplied reference.

The supplied data currently produce **348 trial segments and 6,270 gait
cycles**. Of these trials, 268 pass the broad automatic cycle-count check and 80
are marked `CHECK`; flagged trials are retained so they can be visually reviewed
rather than silently discarded. `Sub07_H` trial 1 cannot be processed as a
complete triplet because its left-insole file is absent.

Join normalized samples to metadata on `cycle_id`. Use participant-wise splits
(for example, leave-one-subject-out), never random cycle-wise splits, because
cycles from the same participant are strongly correlated.

## Completing the seven-class study

Obtain the missing table mapping trials 1-40 and within-trial sections to the
seven classes. Add those labels after checking transition boundaries against
vGRF contacts. Train with participant-wise validation and report per-class
precision, recall, F1, confusion matrices, and macro averages. Report amputee
results separately unless the protocol explicitly supports pooled training.

### Important interpretation of inferred phase labels

The annotated plots use an automatic change point in stride duration. The
steady section with the shorter median stride duration is labelled `SSSW`, the
longer section `SSLW`, and their intervening cycle `SLT` or `LST`. This produces
the requested segmentation for visual review, but step duration is only a proxy
for instructed step length. `phase_summary.csv` records a confidence score; the
labels must be reconciled with the original trial protocol before publication
or supervised model training.

## Earlier exploratory files

`main.py`, `segmentation.py`, `batch_segmentation.py`, and root-level sample
summary CSVs are exploratory work. `run_study1.py` is the reproducible
all-dataset entry point and supersedes hard-coded paths in those files.
