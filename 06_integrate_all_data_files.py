import os
import re
import glob
import pandas as pd

# === SETTINGS ===
DATA_DIR = "documentation"   # <-- change this
OUTPUT_DIR = "r_analysis/data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "combined_Data_with_strategy_and_model.xlsx")

# === HELPERS ===
def parse_model_used(fname: str) -> str:
    """Return 'gpt-5-mini' or 'gpt-5' based on filename."""
    # IMPORTANT: check 'gpt-5-mini' first because it contains 'gpt-5'
    if "gpt-5-mini" in fname:
        return "gpt-5-mini"
    elif "gpt-5" in fname:
        return "gpt-5"
    else:
        raise ValueError(f"Could not determine model from filename: {fname}")

def parse_examples(fname: str) -> int:
    """Return 0, 5, or 25 based on filename."""
    # Use regex to be tolerant of slight name variations
    m = re.search(r"(\b|_)0Examples(\b|_)", fname)
    if m: 
        return 0
    m = re.search(r"(\b|_)5Examples(\b|_)", fname)
    if m: 
        return 5
    m = re.search(r"(\b|_)25Examples(\b|_)", fname)
    if m: 
        return 25
    raise ValueError(f"Could not determine number of examples from filename: {fname}")

def parse_model_provided(fname: str) -> bool:
    """Return True if a model was provided (wTruth_), else False (woTruth_)."""
    if "wTruth_" in fname:
        return True
    if "woTruth_" in fname:
        return False
    raise ValueError(f"Could not determine Model Provided (wTruth_/woTruth_) from filename: {fname}")

def parse_model_created(fname: str) -> bool:
    """Return True if a model was created (wDiagramCreation_), else False."""
    return "wDiagramCreation_" in fname

def strategy_from_flags(model_provided: bool, model_created: bool, examples: int) -> int:
    """
    Map (Model Provided, Model Created, Examples) -> Strategy number (1–9).
    Table (from your spec):
      S1: No,  No,  0
      S2: No,  No,  5
      S3: No,  No, 25
      S4: Yes, No,  0
      S5: Yes, No,  5
      S6: Yes, No, 25
      S7: No,  Yes, 0
      S8: No,  Yes, 5
      S9: No,  Yes, 25
    """
    mp = model_provided
    mc = model_created
    ex = examples

    if not mp and not mc and ex == 0:  return 1
    if not mp and not mc and ex == 5:  return 2
    if not mp and not mc and ex == 25: return 3
    if mp and not mc and ex == 0:      return 4
    if mp and not mc and ex == 5:      return 5
    if mp and not mc and ex == 25:     return 6
    if not mp and mc and ex == 0:      return 7
    if not mp and mc and ex == 5:      return 8
    if not mp and mc and ex == 25:     return 9

    # Any other combo is not defined in your table
    raise ValueError(f"No strategy defined for (Model Provided={mp}, Model Created={mc}, Examples={ex})")

# === MAIN ===
all_rows = []

for path in glob.glob(os.path.join(DATA_DIR, "*.xlsx")):
    fname = os.path.basename(path)

    # Derive metadata from filename
    model_used = parse_model_used(fname)
    examples = parse_examples(fname)
    model_provided = parse_model_provided(fname)
    model_created = parse_model_created(fname)
    strategy = strategy_from_flags(model_provided, model_created, examples)

    # Read 'Data' sheet
    try:
        df = pd.read_excel(path, sheet_name="Data")
    except ValueError as e:
        # 'Data' sheet missing or unreadable — skip with a clear message
        print(f"Skipping (no 'Data' sheet): {fname} — {e}")
        continue

    # Add requested columns
    df["Strategy"] = strategy
    df["Model Used"] = model_used

    # (Optional but helpful) keep source filename for traceability
    df["Source File"] = fname

    all_rows.append(df)

# Combine & save
if not all_rows:
    raise RuntimeError("No files were read. Check DATA_DIR and file patterns.")

combined = pd.concat(all_rows, ignore_index=True)
combined.to_excel(OUTPUT_FILE, index=False)
print(f"Done. Wrote {len(combined):,} rows to:\n{OUTPUT_FILE}")
