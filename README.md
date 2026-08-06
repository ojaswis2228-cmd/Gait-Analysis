# Gait Analysis - Project Guide

## 1. What this folder is for

This folder contains gait (walking) data collected from people wearing:

- **FMG bands** on the left and right thighs. FMG means *force myography*: the bands measure changes in muscle shape/pressure while a person moves.
- **Insole sensors** under each foot. These provide vertical ground-reaction force (**vGRF**) and centre-of-pressure (**CoP**) information.

The project is at the **early analysis / data-preparation stage**. The Python scripts currently demonstrate how to load one FMG recording, find its trigger events, take data around each event, inspect plots, and calculate simple numerical features.

## 2. Research aim described in the included PDF

`Planning two studies from the FMG data collected.pdf` describes two intended machine-learning studies.

1. **Study 1 - gait classification**
   - Classify walking events and conditions such as gait initiation, gait termination, step length, and transitions.
   - The document says the intended model has 7 classes.

2. **Study 2 - force and pressure estimation**
   - Estimate vertical ground-reaction force (vGRF) and centre-of-pressure (CoP) movement from the 8-channel thigh FMG data.
   - This is intended to be studied separately for normal, long, and short steps.

The PDF mentions approximately 360 gait cycles per walking condition, data from healthy and amputee participants, and 40 overground-walking trials. These are the study notes; the folder layout alone does not verify every planned cycle or condition.

## 3. What data is present now

There are **9 subject folders** with **209 data files** (roughly **200 MB** in total):

| Folder | Files | What it appears to represent |
| --- | ---: | --- |
| `Sub01_A` | 6 | Subject 01, A-labelled participant |
| `Sub01_H` | 6 | Subject 01, H-labelled participant |
| `Sub02_A` | 6 | Subject 02, A-labelled participant |
| `Sub02_H` | 9 | Subject 02, H-labelled participant |
| `Sub03_H` | 6 | Subject 03, H-labelled participant |
| `Sub05_H` | 6 | Subject 05, H-labelled participant |
| `Sub06_H` | 120 | Subject 06, H-labelled participant; many smaller trial files |
| `Sub07_H` | 44 | Subject 07, H-labelled participant; many smaller trial files |
| `Sub08_H` | 6 | Subject 08, H-labelled participant |

`H` and `A` appear to follow the healthy/amputee grouping described in the PDF, but that meaning should be confirmed with the data collector before it is used as a formal label.

### Standard recording groups

The PDF explains the usual six-file format for a subject called `X`:

| File pattern | Trials | Contents |
| --- | --- | --- |
| `X_1` | 1-20 | Combined FMG: time, trigger, 8 left-band channels, 8 right-band channels |
| `X_1L` | 1-20 | Left insole: time, trigger, CoP excursion, vGRF |
| `X_1R` | 1-20 | Right insole: time, trigger, CoP excursion, vGRF |
| `X_21` | 21-40 | Combined FMG, same format as `X_1` |
| `X_21L` | 21-40 | Left insole, same format as `X_1L` |
| `X_21R` | 21-40 | Right insole, same format as `X_1R` |

For example, `Sub01_H/abh_1.txt` is a combined FMG recording and `Sub01_H/abh_1L` and `Sub01_H/abh_1R` are its left and right insole companions. Some names differ slightly (`_L`, `_R`, `1L`, `1R`, or no filename extension), especially in `Sub06_H` and `Sub07_H`; software that processes all files will need to handle these naming variations.

### Combined FMG file columns

The existing analysis code expects each valid combined-FMG row to contain **18 numeric values**:

| Column(s) | Meaning |
| --- | --- |
| `Time` | Recording time |
| `Trigger` | Marker signal; a block of `1` values marks a recorded event/trial boundary |
| `L1` to `L8` | Eight channels from the left FMG band |
| `R1` to `R8` | Eight channels from the right FMG band |

The scripts skip the first line as metadata and ignore malformed rows. The left/right companion insole files are not yet processed by the supplied scripts. According to the PDF, their expected columns are time, trigger, CoP excursion, and vGRF.

## 4. What has been done in the code

All scripts currently use the same example file: `Sub01_H/abh_1.txt`. They do not yet loop over the whole dataset or write output files.

| Script | Current job |
| --- | --- |
| `main.py` | Loads the example FMG file, assigns column names, prints shape/statistics and trigger counts, and opens plots for the trigger, `L1`, and the first 3,000 samples of all left channels. |
| `trigger_analysis.py` | Finds each continuous `Trigger == 1` block and prints its start index, end index, and length. |
| `window_extraction.py` | Finds trigger starts and extracts 300 samples before plus 300 samples after each start: a 600-sample window. |
| `feature_extraction.py` | Creates six basic features for every FMG channel in every window. |
| `event_plot.py` | Plots the eight left FMG channels and then the eight right FMG channels around the first trigger (sample 609). |
| `label_finder.py` | Prints the first 50 lines of one left-insole file to inspect its raw structure. It is a diagnostic tool, not a label-generation program. |

### Feature extraction in simple words

For each 600-sample event window, the program looks at every one of the 16 FMG channels and calculates:

1. Mean - average signal value.
2. Standard deviation - how much the signal varies.
3. Variance - another measure of variation.
4. Minimum - lowest value.
5. Maximum - highest value.
6. RMS (root mean square) - overall signal magnitude.

That is **16 channels x 6 features = 96 features per trigger event**.

## 5. Verified example result

The non-plot scripts were run on `Sub01_H/abh_1.txt` using the project logic.

- Raw file lines: **63,713**
- Trigger blocks detected: **36**
- Valid extracted windows: **36**
- Window size: **600 rows x 18 columns**
- Feature matrix: **36 rows x 96 columns**

This means each row of the feature matrix represents one trigger-centred event from this one recording. It is not yet a labelled training dataset.

## 6. How to run the current scripts

### Requirements

Install Python 3 and these packages:

```powershell
python -m pip install pandas numpy matplotlib
```

### Run

Open PowerShell in this folder and run one of the following:

```powershell
python main.py
python trigger_analysis.py
python window_extraction.py
python feature_extraction.py
python event_plot.py
python label_finder.py
```

`main.py` and `event_plot.py` open Matplotlib graphs. Close a graph window to let the script continue/finish.

## 7. Important current limitations

- The input file path is hard-coded to `Sub01_H/abh_1.txt` in every analysis script.
- No script currently processes every subject or trial automatically.
- The insole vGRF/CoP data is not yet aligned with FMG windows or used as a prediction target.
- No event-class labels have been created by the code.
- No machine-learning model has been trained, validated, or tested.
- No features, plots, or cleaned datasets are saved to disk; results are printed or displayed only.
- `event_plot.py` hard-codes the first trigger as sample 609, so it applies only to the current example unless changed.
- The dataset contains naming inconsistencies and one combined sample is named `.txt` while most recordings have no extension. A future batch loader should not rely only on extensions.
- The PDF says there are 8 healthy and 2 amputee participants, while this folder currently has 7 H-labelled and 2 A-labelled subject folders. Confirm whether a healthy subject folder is missing or stored elsewhere.

## 8. Sensible next steps

1. Make one reusable data-loading function that can read any combined FMG file and its matching left/right insole files.
2. Standardise file names or create a metadata table that links subject, trial, condition, FMG file, and insole files.
3. Use triggers to segment all recordings consistently.
4. Align FMG windows with the matching vGRF and CoP values from the insole files.
5. Add verified labels for gait condition/event; do not infer them only from filenames.
6. Save cleaned windows and feature tables as CSV or Parquet files.
7. Split data by participant (not random windows from the same participant) before training machine-learning models, to avoid overly optimistic results.
8. Train and evaluate classification and regression models only after the labels and target alignment have been checked.

## 9. Folder contents besides data and scripts

- `Planning two studies from the FMG data collected.pdf` - short plan describing the two proposed research studies and intended data format.
- `WhatsApp Image 2026-07-30 at 12.02.22 PM.jpeg` - an image supplied with the project; it is not used by the current scripts.

## 10. Short summary

The folder already has a substantial raw gait dataset and a working **single-file FMG exploration pipeline**. It can identify trigger-centred events and turn each event into 96 simple FMG features. The main remaining work is to scale this to all data, connect FMG with the insole ground-force/pressure data, create reliable labels, save a clean dataset, and build/evaluate machine-learning models.
