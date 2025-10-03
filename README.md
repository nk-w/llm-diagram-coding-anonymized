# LLM-Based Coding of Student Causal Diagrams (Anonymized for Review)

> **For Reviewers — Inspection Only**  
> This repository is anonymized for peer review. It is provided **solely for code and workflow inspection**. Execution is **not supported** in this repo bcause we do not have permission to share the dataset used to run this analysis.

---

## Scope & Limitations

- **Non-Executable Code:** You can examine code structure, workflow design, schemas, and documentation. Running scripts or reproducing results is **not possible** in this anonymized version because the original dataset is not included.
- **Data Access:** The original dataset of student causal diagrams is **not included** due to privacy and license restrictions. Derived files etc. that would reveal or depend on the dataset are also omitted.

---

## Project Overview

This repository organizes the end-to-end workflow for evaluating how Large Language Models (LLMs) code students’ causal diagrams across prompting strategies, model families, and cost constraints.

- **Python components** orchestrate batch prompting, parsing of responses, schema validation, and metric preparation.  
- **R/Quarto components** define Bayesian follow-up analyses and figure/table generation logic.

The code is presented to make the methodology **transparent** and the pipeline design **auditable**, even though it cannot be executed here.

---

## Repository Map (Reviewer-Focused)

| Path | Purpose | Reviewer Notes |
| --- | --- | --- |
| `Batch Input Files/` | Structure used for JSONL payloads to LLM APIs | Shows expected payload layout; not populated here |
| `Batch Response Files/` | Structure for returned batch outputs | Not populated here |
| `Data/` | Placeholder for source datasets | Not included; code references document expected schema/paths |
| `Texts/` | Reading passages used by students in original studies | Included as plain text; filenames referenced in prompts |
| `Prompts/` | Prompt templates/variants | Inspect structure, variables, and naming conventions |
| `documentation/` | Structure for derived tables/figures | Not populated here |
| `model_diagrams.json` | Model diagram representations | Defines golden standard diagrams |
| `response_schema_v0.1*.json` | Response validation schemas | Inspect fields, constraints, and evolution across versions |
| `r_analysis/` | R/Quarto analysis code | Review model formulas, processing logic, and figure scripts |
| `r_analysis/scripts/*.qmd` | Analysis steps (cleaning, models, figures) | Shows intended sequence and outputs without data |
| `r_analysis/figures/`, `tables/`, `models/`, `logs/` | Output targets | Present as structure only in this artifact |

---

## Python Pipeline Description 

- **01_batch_request.py**: Loads the master Excel file, filters down to the Desar dataset with only “g” or “c” codes, then groups rows into student/text diagrams. Through a short menu the user picks one of nine preset strategies that swap prompts, notes, schema files, truth labels, and the count of in-context examples. For each randomly selected student diagram, the script rebuilds the base model template, drops truth fields when hidden, adds the student’s answers, and—if examples are requested—pulls same-text examples at random, builds inputs from model_diagrams.json, and fills expected outputs using response.json. Prompts stitch together system text, the original passage from Texts/, the student diagram, optional examples, and researcher notes. Finally, it writes a JSONL batch file, and can upload or submit it to OpenAI depending on user confirmation.
- **02_batch_retrieve.py**: Lists recent OpenAI batch jobs, groups them by status, and prints simple summaries. Reviewers (or operators) type the indices of finished jobs to download; the script pulls each output file and saves it under Batch Response Files/ using the original batch description. It also parses the JSON lines so you know each response is a structured content block ready for analysis.
- **03.1_batch_process.py**: Handles a single downloaded JSONL file. It parses every response, records prompt and completion token counts, and pulls the original student answers via the same filter/group helpers as the request script to ensure row alignment. For each response it compares the model’s extraction, position, and “correct position” fields to the human coding, produces confusion-matrix labels, then calculates accuracy, precision, recall, F1, and Cohen’s kappa. Token totals feed a per-model cost estimate, and everything is written into an Excel workbook with a “Measures” summary sheet plus a detailed “Data” sheet.
- **03.2_batch_process_loop.py**: Automates the previous step by scanning the whole Batch Response Files/ folder. It reuses the same comparison logic but adds zero-division guards so odd or empty files don’t crash the run. Results are saved one workbook per input file inside documentation/, and progress messages flag which files were processed.
- **04_explore_dataset.py**: A quick-look tool for the raw Excel. After adding participant and diagram IDs, it reports how many rows, diagrams, and students are in the Desar subset, summarizes response lengths, and prints per-text code counts. It relies on the user to supply the data path at runtime and prints the stats to the console for reporting.
- **05_explore_results.py**: Designed to compare multiple processed Excel files. You list file names manually in the settings list, and for each one it reads the “Measures” sheet, extracts metrics, parses the filename to recover model, truth label, example count, and diagram-creation flags, then assembles an overview table with averages added.
- **06_integrate_all_data_files.py**: Sweeps documentation/*.xlsx, reads the “Data” sheet from each, and tags every row with strategy numbers 1–9, the model used, and the source filename based on naming conventions (for example, it checks for wTruth_, wDiagramCreation_, 0Examples, etc.). The combined dataset is written to r_analysis/data/combined_Data_with_strategy_and_model.xlsx, giving the R analysis code a single consolidated input. Misnamed files trigger clear exceptions so issues show up immediately.

---

## R Pipeline Description

- **r_analysis/scripts/01_cleaning_data.qmd**: loads the combined Excel created by the Python pipeline, trims unused columns, and splits the UUID into student, class, and text identifiers. It confirms the UUID pattern, inventories unique IDs, and builds helper flags for whether the gold-standard diagram was provided or created and how many examples were given. Problematic rows (missing extraction agreement or odd LLM_CorrectPosition values like 2.3) are filtered out, a text_box_id is added, and factor/logical types are enforced before the cleaned dataset is exported to data/data_brms_analysis.xlsx.
- **r_analysis/scripts/02_brms_analysis.qmd**: prepares and runs the Bayesian GLMMs. After ensuring required packages and columns, it keeps only GPT‑5 model runs, checks coverage of all strategy combinations, and splits the data into two analysis frames: one for extraction  and one for positioning. Each frame feeds a GLMM model in brms with student and text-box random intercepts. The script first fits a small “smoke test,” then the full models, emits odds-ratio tables, and calculates predicted probabilities plus deltas from the baseline “no model provided/created, 0 examples” setup.
- **r_analysis/scripts/03_descriptives.qmd**: delivers descriptives based on the analysis datasets. It rebuilds confusion-matrix counts per strategy and model, converts them into accuracy, precision, recall, F1, and κ, and saves a CSV summarizing both idea extraction and positioning. It also reports quick stats (best-performing strategy, distribution summaries) to support the narrative sections.
- **r_analysis/scripts/04_figures.qmd**: uses the saved brms fits to create figures for the manuscript. It reloads the modelling data, reconstructs the same analysis frames, and regenerates predicted-probability grids and main-effect odds ratios. From there it produces heatmaps, interaction lines, forest plots, and random-effect density plots, exporting each to PNG/PDF under figures/.

---

## Anonymization Notes

- Identifying details (names, affiliations, URLs, emails) have been replaced with neutral placeholders.  
- Binary/document metadata and notebook outputs have been removed in this review version of the repo.  
- License and citation metadata will be restored in the final version following review policy.