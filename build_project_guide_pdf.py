#!/usr/bin/env python3
"""Build the plain-language project presentation guide PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Image, KeepTogether, ListFlowable, ListItem,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "pdf" / "Gait_Analysis_Project_Presentation_Guide.pdf"
ANNOTATED = ROOT / "output" / "study1" / "annotated_trials" / "Sub01_H_trial_01_annotated.png"
COUNTS = ROOT / "output" / "study1" / "plots" / "all_subject_cycle_counts.png"

NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#2F6B9A")
LIGHT = colors.HexColor("#EAF3F8")
CYAN = colors.HexColor("#D8EEF2")
ORANGE = colors.HexColor("#E8893A")
GRAY = colors.HexColor("#5E6B75")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D3DCE3"))
    canvas.line(1.5 * cm, 1.2 * cm, 19.5 * cm, 1.2 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(1.5 * cm, 0.8 * cm, "Gait Analysis - Study 1 presentation guide")
    canvas.drawRightString(19.5 * cm, 0.8 * cm, f"Page {doc.page}")
    canvas.restoreState()


def bullets(items, style):
    return ListFlowable(
        [ListItem(Paragraph(item, style), leftIndent=12) for item in items],
        bulletType="bullet", leftIndent=18, bulletFontName="Helvetica",
        bulletFontSize=8, spaceAfter=8,
    )


def info_box(title, text, styles, background=LIGHT):
    table = Table([[Paragraph(f"<b>{title}</b><br/>{text}", styles["BodyText"])]], colWidths=[17.5 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), background),
        ("BOX", (0, 0), (-1, -1), 0.7, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleWhite", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=28, leading=34, textColor=colors.white, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="SubtitleWhite", parent=styles["Normal"], fontSize=13, leading=19,
                              textColor=colors.white, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="H1Navy", parent=styles["Heading1"], fontName="Helvetica-Bold",
                              fontSize=21, leading=25, textColor=NAVY, spaceAfter=10))
    styles.add(ParagraphStyle(name="H2Blue", parent=styles["Heading2"], fontName="Helvetica-Bold",
                              fontSize=14, leading=18, textColor=BLUE, spaceBefore=8, spaceAfter=5))
    styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], fontName="Helvetica",
                              fontSize=10.2, leading=15, textColor=colors.HexColor("#24323D"), spaceAfter=7))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.7, leading=12,
                              textColor=GRAY))
    styles.add(ParagraphStyle(name="Say", parent=styles["BodyText"], fontName="Helvetica-Oblique",
                              fontSize=10.5, leading=15, textColor=NAVY))
    body = styles["Body"]

    doc = BaseDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=1.6 * cm, leftMargin=1.6 * cm,
                          topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                          title="Gait Analysis Project Presentation Guide")
    frame = Frame(doc.leftMargin, doc.bottomMargin + 0.4 * cm, doc.width, doc.height - 0.4 * cm, id="main")
    doc.addPageTemplates(PageTemplate(id="guide", frames=frame, onPage=footer))
    story = []

    cover = Table([[Paragraph("GAIT ANALYSIS", styles["TitleWhite"]),],
                   [Paragraph("Study 1: FMG-based gait segmentation<br/>Simple project explanation and presentation guide",
                              styles["SubtitleWhite"])]], colWidths=[17.8 * cm], rowHeights=[4.2 * cm, 3.8 * cm])
    cover.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("BOX", (0, 0), (-1, -1), 0, NAVY)]))
    story += [Spacer(1, 3.1 * cm), cover, Spacer(1, 1.2 * cm),
              Paragraph("What this guide helps us do", styles["H2Blue"]),
              Paragraph("Understand the complete project, explain our processing steps, interpret the final segmentation plots, and answer common questions during a discussion with sir.", body),
              info_box("One-line project summary", "We used thigh FMG signals and foot-insole force signals to divide walking recordings into meaningful gait sections and individual gait cycles.", styles, CYAN),
              Spacer(1, 1.4 * cm), Paragraph("Prepared from the supplied Study 1 brief and the processed project dataset.", styles["Small"]), PageBreak()]

    story += [Paragraph("1. What is this project about?", styles["H1Navy"]),
              Paragraph("The project studies how a person's thigh muscles change shape and pressure during walking. Sensors placed around the thigh record these changes as <b>force myography (FMG)</b>. Insoles under the feet simultaneously measure foot force and pressure location.", body),
              info_box("Main idea", "Different walking actions create different signal patterns. If a computer learns these patterns, an assistive device can understand what the user is trying to do.", styles),
              Paragraph("Why is it useful?", styles["H2Blue"]),
              bullets(["A prosthetic or assistive device could recognize when a person starts or stops walking.",
                       "It could recognize short and long steps and prepare for a change in walking style.",
                       "The same sensor data can later help estimate vertical ground reaction force and center of pressure."], body),
              Paragraph("The two studies in the supplied brief", styles["H2Blue"]),
              Table([["Study", "Purpose"],
                     ["Study 1", "Classify gait initiation, termination, steady walking, step length and transitions."],
                     ["Study 2", "Estimate vertical ground reaction force and center-of-pressure movement from FMG."]],
                    colWidths=[2.5 * cm, 15 * cm], style=TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#BCC8D0")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("FONTSIZE", (0, 0), (-1, -1), 9.5), ("LEADING", (0, 0), (-1, -1), 13),
                        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)])),
              Spacer(1, .4 * cm), Paragraph("Our present work focuses on <b>Study 1 segmentation</b>. We have not yet trained the final machine-learning classifier.", body), PageBreak()]

    story += [Paragraph("2. What data did we receive?", styles["H1Navy"]),
              Paragraph("The project folder contains recordings from <b>8 healthy participants</b> and <b>2 participants with amputation</b>. Files are stored differently for different subjects: some contain many trials in one recording, while others contain one trial per file.", body),
              Paragraph("Signals in each recording", styles["H2Blue"]),
              Table([["Signal", "Meaning", "Use in our work"],
                     ["Time", "Recording time", "Synchronize events and estimate cycle duration"],
                     ["Trigger", "Marks trial boundaries", "Separate a long recording into walking trials"],
                     ["8 left FMG channels", "Pressure around the left thigh", "Left-side gait pattern"],
                     ["8 right FMG channels", "Pressure around the right thigh", "Right-side gait pattern"],
                     ["vGRF", "Vertical ground reaction force", "Detect when the foot contacts the ground"],
                     ["CoP", "Center of pressure excursion", "Describe movement of pressure under the foot"]],
                    colWidths=[3.4 * cm, 6.3 * cm, 7.8 * cm], repeatRows=1,
                    style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                      ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#C6D0D7")),
                                      ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                      ("FONTSIZE", (0, 0), (-1, -1), 8.8), ("LEADING", (0, 0), (-1, -1), 12),
                                      ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                                      ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)])),
              Spacer(1, .5 * cm),
              info_box("File quality issue we handled", "Several files begin with an incomplete row, naming is inconsistent, one folder is nested twice, some subjects use aggregate files, and some use individual-trial files. Our reader accepts only complete numeric rows and discovers valid FMG-left-right triplets automatically.", styles),
              Spacer(1, .3 * cm), Paragraph("Sub07_H trial 1 is not processed as a complete triplet because its left-insole file is missing.", styles["Small"]), PageBreak()]

    story += [Paragraph("3. What does segmentation mean?", styles["H1Navy"]),
              Paragraph("Segmentation means cutting one long signal into smaller, meaningful pieces. We perform it at three levels.", body),
              Table([["Level", "What we separate", "Example"],
                     ["1. Recording", "Separate individual walking trials using trigger markers", "Trial 1, Trial 2, ..."],
                     ["2. Gait cycle", "Separate one stride from the next using vGRF foot contacts", "Heel strike to the next heel strike"],
                     ["3. Movement phase", "Assign walking meaning to groups of cycles", "GI, SSSW, SLT, SSLW, GT"]],
                    colWidths=[3 * cm, 9 * cm, 5.5 * cm], style=TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#BCC8D0")),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9.2), ("LEADING", (0, 0), (-1, -1), 13),
                        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)])),
              Paragraph("The movement labels", styles["H2Blue"]),
              bullets(["<b>QS:</b> quiet standing before walking.", "<b>GI:</b> gait initiation - the person starts walking.",
                       "<b>SSSW:</b> steady-state short-step walking.", "<b>SSLW:</b> steady-state long-step walking.",
                       "<b>SLT:</b> transition from short steps to long steps.", "<b>LST:</b> transition from long steps to short steps.",
                       "<b>GT:</b> gait termination - the person stops walking."], body),
              info_box("Simple example", "A trial may follow this order: quiet standing -> gait initiation -> short steps -> short-to-long transition -> long steps -> gait termination.", styles, CYAN), PageBreak()]

    story += [Paragraph("4. How our segmentation pipeline works", styles["H1Navy"]),
              Paragraph("The complete process is automatic and repeatable:", body),
              bullets(["<b>Read:</b> load complete FMG and insole rows without changing the raw files.",
                       "<b>Find trials:</b> detect high trigger pulses and use marker pairs as trial boundaries.",
                       "<b>Clean vGRF:</b> use a short rolling median to reduce noise.",
                       "<b>Detect foot contacts:</b> use adaptive thresholds based on each trial's own force range.",
                       "<b>Handle sensor direction:</b> test both force polarities because one supplied channel is inverted.",
                       "<b>Align devices:</b> map insole contacts to FMG using elapsed time because their sampling rates differ.",
                       "<b>Create cycles:</b> cut the eight FMG channels between consecutive contacts.",
                       "<b>Normalize:</b> resample every cycle to 101 points, representing 0-100% of a gait cycle.",
                       "<b>Find transition:</b> locate the strongest change in stride duration inside the trial.",
                       "<b>Label and plot:</b> create GI, steady walking, transition and GT sections with CoP and vGRF."], body),
              info_box("Why normalize to 101 points?", "People walk at different speeds, so raw cycles have different numbers of samples. Converting each cycle to 0-100% gives every machine-learning example the same length.", styles),
              Paragraph("Quality control", styles["H2Blue"]),
              Paragraph("A trial is marked <b>OK</b> when both feet have a broadly reasonable number of cycles. A trial is marked <b>CHECK</b> when the count is unusual. CHECK does not mean the data are deleted; it means a person should inspect that trial.", body), PageBreak()]

    story += [Paragraph("5. What did we produce?", styles["H1Navy"]),
              Table([["Result", "Count"], ["Subjects represented", "10"], ["Valid recording triplets", "71"],
                     ["Walking trial segments", "348"], ["Segmented gait cycles", "6,270"],
                     ["Normalized signal rows", "633,270"], ["Trials passing broad QA", "268"],
                     ["Trials marked for review", "80"], ["Annotated trial figures", "343"]],
                    colWidths=[11.5 * cm, 6 * cm], style=TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("ALIGN", (1, 1), (1, -1), "CENTER"),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]), ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#C6D0D7")),
                        ("FONTSIZE", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7), ("LEFTPADDING", (0, 0), (-1, -1), 8)])),
              Spacer(1, .5 * cm),
              Image(str(COUNTS), width=16.5 * cm, height=7.5 * cm),
              Paragraph("Figure: Number of successfully segmented gait cycles for each participant and side.", styles["Small"]), PageBreak()]

    story += [Paragraph("6. How to read the final annotated plot", styles["H1Navy"]),
              Image(str(ANNOTATED), width=18 * cm, height=10.1 * cm),
              Paragraph("Example annotated output. The top panel is the left side and the bottom panel is the right side.", styles["Small"]),
              Spacer(1, .25 * cm),
              bullets(["Each colored curve represents one of eight FMG channels, CoP or vGRF.",
                       "The horizontal axis joins normalized gait cycles in their original order.",
                       "The vertical axis uses normalized amplitude so signals with different units can be compared visually.",
                       "Dashed vertical lines show detected movement-section boundaries.",
                       "GI and GT are the first and last complete gait cycles.",
                       "SSSW and SSLW are the two steady sections; SLT or LST is their transition."], body),
              Paragraph("What to say while showing this figure", styles["H2Blue"]),
              info_box("Suggested explanation", "This figure shows that we first divided the walking trial into individual strides using the insole force signal. We then compared stride duration before and after the main change point. The program marked gait initiation, the two steady walking sections, the transition, and gait termination. All eight FMG channels, CoP and vGRF are shown together so we can visually check whether the boundaries match changes in the signals.", styles, CYAN), PageBreak()]

    story += [Paragraph("7. Important limitation - explain this honestly", styles["H1Navy"]),
              Paragraph("The supplied PDF describes the intended classes and approximate data counts, but it does <b>not</b> provide the original trial-by-trial protocol table. Therefore, we can confidently measure trigger boundaries, foot contacts, gait cycles and stride durations, but the exact instructed short/long label is not directly stored in the provided files.", body),
              info_box("What the software currently does", "It finds the strongest stride-duration change. The section with shorter median stride duration is provisionally called SSSW, the longer section SSLW, and the boundary SLT or LST. Every result receives a confidence score.", styles, colors.HexColor("#FFF0DF")),
              Paragraph("Why this matters", styles["H2Blue"]),
              Paragraph("Step duration is a useful clue, but it is not the same measurement as physical step length. The median automatic confidence is modest. Before publishing results or training a supervised seven-class model, the inferred labels should be matched with sir's original trial protocol or experiment log.", body),
              Paragraph("What remains fully valid even without that table", styles["H2Blue"]),
              bullets(["Raw-file reading and inventory", "Trigger-based trial segmentation", "vGRF contact detection",
                       "FMG gait-cycle extraction", "101-point normalization", "Cycle counts, durations and QA flags",
                       "Visual annotated outputs for review"], body),
              Paragraph("Best sentence to use with sir", styles["H2Blue"]),
              Paragraph('"We completed the signal and gait-cycle segmentation. We also created provisional phase labels using stride-duration change points. We need the original trial condition mapping to verify the short/long class names before model training."', styles["Say"]), PageBreak()]

    story += [Paragraph("8. Files generated and what they mean", styles["H1Navy"]),
              Table([["File or folder", "Purpose"],
                     ["dataset_inventory.csv", "Lists the source FMG/left/right file triplets and totals."],
                     ["trial_summary.csv", "One row per trial with contact counts, cycle counts and OK/CHECK status."],
                     ["cycle_metadata.csv", "One row per gait cycle with subject, trial, side, indices and duration."],
                     ["cycles_normalized_101.csv", "Model-ready 101-point FMG, CoP and vGRF values."],
                     ["cycle_phase_labels.csv", "GI, SSSW/SSLW, SLT/LST and GT label for each cycle."],
                     ["phase_summary.csv", "Transition cycle, direction, duration change and confidence."],
                     ["annotated_trials/", "343 visual trial-level segmentation figures."],
                     ["run_study1.py", "Runs data discovery, trial segmentation and gait-cycle extraction."],
                     ["create_desired_segmentation.py", "Creates phase labels and annotated plots."],
                     ["README.md", "Technical instructions, method, outputs and limitations."]],
                    colWidths=[6 * cm, 11.5 * cm], repeatRows=1, style=TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#C6D0D7")),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8.8), ("LEADING", (0, 0), (-1, -1), 12),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)])),
              Spacer(1, .5 * cm), info_box("Reproducibility", "The original data are never overwritten. Running the scripts again recreates the CSV outputs and figures using the same documented method.", styles), PageBreak()]

    story += [Paragraph("9. A simple presentation script", styles["H1Navy"]),
              Paragraph("Opening", styles["H2Blue"]),
              Paragraph('"Our project uses force myography signals from thigh bands together with left and right insole signals. The aim of Study 1 is to identify important walking states that can later be used to control an assistive device."', styles["Say"]),
              Paragraph("Dataset", styles["H2Blue"]),
              Paragraph('"The dataset contains eight FMG channels per thigh, trigger markers, center of pressure and vertical ground reaction force. We processed recordings from eight healthy and two amputee participants."', styles["Say"]),
              Paragraph("Method", styles["H2Blue"]),
              Paragraph('"We used trigger markers to find trials and vGRF to detect foot contacts. Consecutive contacts define gait cycles. Each FMG cycle was converted to 101 points so cycles from different walking speeds have the same size."', styles["Say"]),
              Paragraph("Output", styles["H2Blue"]),
              Paragraph('"We obtained 348 trial segments and 6,270 gait cycles. The output plots show all eight FMG channels, CoP and vGRF with gait initiation, steady sections, transition and termination."', styles["Say"]),
              Paragraph("Limitation and next step", styles["H2Blue"]),
              Paragraph('"The original trial condition table was not included, so short-versus-long direction is currently inferred from stride duration and stored with confidence. Our next step is to verify these labels using the experiment protocol and then train the seven-class model using subject-wise validation."', styles["Say"]), PageBreak()]

    story += [Paragraph("10. Questions sir may ask", styles["H1Navy"]),
              Paragraph("Why did you use vGRF for segmentation?", styles["H2Blue"]),
              Paragraph("vGRF changes clearly when the foot loads and unloads, so it gives more direct foot-contact boundaries than FMG alone.", body),
              Paragraph("Why use adaptive thresholds?", styles["H2Blue"]),
              Paragraph("Force range differs across people, feet and trials. A threshold calculated from each trial is more robust than one fixed number.", body),
              Paragraph("Why 101 samples?", styles["H2Blue"]),
              Paragraph("They represent 0 to 100% of a gait cycle, including both endpoints, and give every example the same shape for machine learning.", body),
              Paragraph("Why are some trials marked CHECK?", styles["H2Blue"]),
              Paragraph("Their detected cycle count is outside the broad expected range. We keep them for manual review instead of silently deleting data.", body),
              Paragraph("Can we train the seven-class model now?", styles["H2Blue"]),
              Paragraph("The signal processing is ready, but the provisional step-length labels should first be verified against the missing trial protocol.", body),
              Paragraph("How should training and testing be split?", styles["H2Blue"]),
              Paragraph("Split by participant, not randomly by cycle. Cycles from the same person are similar, so random cycle splitting can give an unrealistically high score.", body),
              Paragraph("What should we report for the classifier?", styles["H2Blue"]),
              Paragraph("A confusion matrix and per-class precision, recall and F1 score, plus macro averages. Healthy and amputee performance should also be examined separately.", body), PageBreak()]

    story += [Paragraph("11. Next steps", styles["H1Navy"]),
              bullets(["Obtain the original trial protocol or condition sheet from sir.",
                       "Verify every short/long and transition label using the protocol.",
                       "Review the 80 CHECK trials and correct or exclude only with a documented reason.",
                       "Create participant-wise training, validation and test splits.",
                       "Start with a simple baseline model before trying complex deep-learning models.",
                       "Report seven-class metrics and confusion matrices.",
                       "Compare healthy and amputee performance and document sensor/data limitations."], body),
              Spacer(1, .5 * cm),
              info_box("Current project status", "Data discovery: complete | Trial segmentation: complete | Gait-cycle segmentation: complete | Normalization: complete | Annotated plots: complete | Protocol label verification: pending | Seven-class model training: pending", styles, CYAN),
              Spacer(1, 1 * cm),
              Paragraph("Final takeaway", styles["H2Blue"]),
              Paragraph("We have built a reproducible pipeline that converts difficult raw FMG and insole recordings into organized trials, gait cycles, normalized model-ready signals, quality-control tables and understandable annotated figures. The key remaining requirement is verification of the experimental class labels before machine-learning evaluation.", body),
              Spacer(1, 1 * cm), Paragraph("End of guide", ParagraphStyle(name="End", parent=styles["Heading2"], alignment=TA_CENTER, textColor=NAVY))]

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
