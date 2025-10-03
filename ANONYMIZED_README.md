# LLM-Based Coding of Student Causal Diagrams

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Study Status: Published](https://img.shields.io/badge/Study-Under_review-blue)
![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)
![R 4.3+](https://img.shields.io/badge/R-4.3+-276DC3.svg?logo=r&logoColor=white)

Automated pipeline and Bayesian analysis toolbox for benchmarking LLM coding of student causal diagrams.

## Executive Summary

This project evaluates how Large Language Models (LLMs) code students' causal diagrams across prompting strategies, model families, and cost constraints. The repository bundles the full workflow: Python scripts orchestrate OpenAI batch runs, data wrangling, and metric reporting, while an embedded R/Quarto project (`r_analysis`) conducts Bayesian follow-up analyses and visualization.

- **Quick links**: [Python Workflow](#python-workflow) · [Data Governance](#data-governance) · [Result Artifacts](#result-artifacts) · [Embedded R Analysis](#embedded-r-analysis)

### Workflow at a Glance
1. Configure prompts, inputs, and batch jobs with the Python scripts in numerical order (`01_` → `06_`).
2. Collect and reconcile OpenAI batch responses into structured metrics and schema-compliant JSONL files.
3. Generate Excel dashboards summarizing accuracy, agreement, and cost for each strategy.
4. Dive deeper inside `r_analysis` to fit Bayesian multilevel models, visualise effects, and export publication-ready tables/figures.

## Repository Map

| Path | Purpose | Highlights |
| --- | --- | --- |
| `Batch Input Files/` | Generated JSONL payloads sent to the OpenAI Batch API | Output directory populated after runs (`Archive/` holds retired jobs) |
| `Batch Response Files/` | Raw batch outputs returned by OpenAI | Empty until batches are retrieved; mirrors input naming inside `ARCHIVE/` |
| `Data/` | Placeholder for source datasets of student diagram codings | We do not have the rights to share the data publicly, which is why it is not provided here |
| `Texts/` | Texts students used when constructing diagrams | Plain-text Dutch articles (`Beton.txt`, `Suez.txt`, …) |
| `Prompts/` | Prompt templates and notes for batch runs | Variants for truth inclusion, examples, and diagram creation |
| `documentation/` | Derived Excel workbooks with metrics and comparisons | Holds documentation for each strategy |
| `model_diagrams.json` | Canonical diagram representations consumed by prompts | Aligns Python pipeline with evaluation schema |
| `response_schema_v0.1*.json` | Schemas validating batch responses | `_wDiagramCreation` variant captures extra diagram outputs |
| `r_analysis/` | Self-contained R/Quarto project for Bayesian modelling | Scripts, Projet structure |

## Python Workflow

### Environment Setup
- Install Python 3.10+ and create a virtual environment: `python -m venv .venv && source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows).
- Install dependencies: `pip install -r requirements.txt`.
- Export your OpenAI API key via `export OPENAI_API_KEY=...` (or set in your shell profile / `.env`).

### Step-by-Step Pipeline
1. `01_batch_request.py` – collect user choices (prompt variant, sample size, model) and build JSONL batch payloads in `Batch Input Files/`.
2. `02_batch_retrieve.py` – monitor OpenAI batch jobs and download completed responses into `Batch Response Files/`.
3. `03.1_batch_process.py` & `03.2_batch_process_loop.py` – parse responses, align them with human-coded ground truth, compute extraction/position metrics, and optionally loop over multiple files.
4. `04_explore_dataset.py` – inspect dataset distributions and surface descriptive statistics prior to modelling.
5. `05_explore_results.py` – optional, manual comparison notebook; populate the `settings` list before running to export custom Excel summaries to `documentation/`.
6. `06_integrate_all_data_files.py` – merge processed outputs into a combined Excel in `documentation/`; follow with `r_analysis/scripts/01_cleaning_data.qmd` to rebuild `r_analysis/data/data_brms_analysis.xlsx`.

### Configuration Tips
- Prompt variants live in `Prompts/`; update or add templates when experimenting with new instructions.
- `model_diagrams.json` controls the canonical reference diagrams shown to models—maintain schema compatibility when editing.
- Response validation is governed by `response_schema_v0.1*.json`; adjust these if you introduce new response fields.
- Large batch runs benefit from organising completed JSONL files into the provided `Archive` folders to keep the workspace lean.
- OpenAI API rate limits need to be conisdered. Depending on API Tier available, the user might need to request the LLM evaluation in groups of a couple of batches at a time. More information can be found at https://platform.openai.com/docs/guides/rate-limits. 

## Data Governance
- Source data is excluded because we do not own the rights to publish this dataset. 
- `Texts/*.txt` store the original reading passages. When adding new texts, keep filenames short and reference them consistently in your prompts and diagrams.
- Generated artifacts in `Batch Input Files/`, `Batch Response Files/`, and `documentation/` are not provided because they contain (parts of) the dataset.
- Derived datasets in `r_analysis/data/` are produced in two steps: `06_integrate_all_data_files.py` updates `combined_Data_with_strategy_and_model.xlsx`, and `r_analysis/scripts/01_cleaning_data.qmd` writes `data_brms_analysis.xlsx`.

## Result Artifacts
- Each `.jsonl.xlsx` file in `documentation/` summarises a single strategy/model combination with a `Measures` sheet (metrics plus token cost rows) and a `Data` sheet containing row-level confusion-matrix fields.
- Filenames follow `YYYY-MM-DD_Strategy_Model_ModelSize_nN.jsonl.xlsx`, matching the originating JSONL files for easy traceability.
- The `ARCHIVE/` subfolder can store superseded outputs; keep only current analyses at the top level to simplify automation.
- Visual summaries generated in `r_analysis/figures/` complement the Excel workbooks and can be embedded directly into manuscripts.

## Embedded R Analysis

Treat `r_analysis/` as a dedicated RStudio/Quarto subproject.

### Setup
- Required tooling: R 4.3+, Quarto CLI, and (optionally) RStudio. Install dependencies on first run by opening each `.qmd` file; the scripts auto-install needed packages (`tidyverse`, `brms`, `cmdstanr`, `bayesplot`, `posterior`, `emmeans`, `broom.mixed`, `performance`, `here`, `readxl`, `janitor`, `data.table`).
- Ensure `cmdstanr` is configured (`cmdstanr::install_cmdstan()`); models depend on Stan backend availability.
- Set the working directory via the provided project file `r_analysis.Rproj` for reliable `here::here()` paths.

### Workflow
1. `scripts/01_cleaning_data.qmd` – loads `data/combined_Data_with_strategy_and_model.xlsx`, cleans identifiers, and prepares analysis tables.
2. `scripts/02_brms_analysis.qmd` – fits Bayesian multilevel models for extraction and position agreement, saving fitted draws to `models/` and generating posterior summaries.
3. `scripts/03_descriptives.qmd` – produces descriptive tables and confusion-matrix summaries, exporting CSVs to `tables/`.
4. `scripts/04_figures.qmd` – generates publication-ready figures from the saved BRMS fits in `models/`.

### Outputs
- Figures (`figures/*.png`, `.zip`) include density overlays, forest plots, and heatmaps.
- Tables (`tables/*.csv`) capture odds ratios, predicted probabilities, and observed metrics for easy import into LaTeX or Word.
- Model objects (`models/*.rds`) are serialised fits suitable for further post-processing or simulation.
- Logs land in `logs/` (currently placeholder `.gitkeep`), where you can configure knitr/Quarto to write build outputs if desired.

## Appendix

Appendix excluded for anonymization purposes
