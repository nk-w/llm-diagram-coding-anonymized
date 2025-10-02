import pandas as pd


def load_data(file_path):
    """Load data from an Excel file."""
    return pd.read_excel(file_path, sheet_name="Measures")

def create_overview_data(settings):
    # Setup Dict to capture all data 
    overview_data = {
        "setting": [],
        "model": [],
        "model diagram": [],
        "diagram creation": [],
        "examples": [],
        "Accuracy_E": [],
        "F_1_E": [],
        "Precision_E": [],
        "Recall_E": [],
        "Kappa H-M_E": [],
        "TP_E": [],
        "FN_E": [],
        "FP_E": [],
        "TN_E": [],
        "Accuracy_P": [],
        "F_1_P": [],
        "Precision_P": [],
        "Recall_P": [],
        "Kappa H-M_P": [],
        "TP_P": [],
        "FN_P": [],
        "FP_P": [],
        "TN_P": [],
        "Input Cost": [],
        "Output Cost": [],
        "Total Cost": [],
        "Cost per Diagram": []
    }

    # Loop through files to extract relevant information
    for idx, setting in enumerate(settings):
        ## Load in Dataframe Measure Sheet
        measures = load_data(file_path=f"documentation/{setting}")
        
        ## Extract Relevant Information in "Measures Sheet" and store in overview_data dict#
        overview_data["diagram creation"].append("yes" if "wDiagramCreation" in setting else "no")
        if "wDiagramCreation" in setting:
            overview_data["model"].append(setting.split("_")[6].replace("gpt-", "").replace("-2024-07-18", "").replace("-2024-08-06", ""))
            overview_data["model diagram"].append("yes" if setting.split("_")[2] == "wTruth" else "no")
            overview_data["examples"].append(setting.split("_")[3].replace("Examples", ""))
        else:
            overview_data["model"].append(setting.split("_")[5].replace("gpt-", "").replace("-2024-07-18", "").replace("-2024-08-06", ""))
            overview_data["model diagram"].append("yes" if setting.split("_")[2] == "wTruth" else "no")
            overview_data["examples"].append(setting.split("_")[3].replace("Examples", ""))

        overview_data["setting"].append(f"S {idx+1}")
        
        ### Extraction Data (E)
        overview_data["Accuracy_E"].append(measures.iloc[1, 1])
        overview_data["F_1_E"].append(measures.iloc[2, 1])
        overview_data["Precision_E"].append(measures.iloc[3, 1])
        overview_data["Recall_E"].append(measures.iloc[4, 1])
        overview_data["Kappa H-M_E"].append(measures.iloc[7, 1])
        overview_data["TP_E"].append(measures.iloc[8, 1])
        overview_data["FN_E"].append(measures.iloc[9, 1])
        overview_data["FP_E"].append(measures.iloc[10, 1])
        overview_data["TN_E"].append(measures.iloc[11, 1])
        
        ### Position Data (P)
        overview_data["Accuracy_P"].append(measures.iloc[14, 1])
        overview_data["F_1_P"].append(measures.iloc[15, 1])
        overview_data["Precision_P"].append(measures.iloc[16, 1])
        overview_data["Recall_P"].append(measures.iloc[17, 1])
        overview_data["Kappa H-M_P"].append(measures.iloc[20, 1])
        overview_data["TP_P"].append(measures.iloc[21, 1])
        overview_data["FN_P"].append(measures.iloc[22, 1])
        overview_data["FP_P"].append(measures.iloc[23, 1])
        overview_data["TN_P"].append(measures.iloc[24, 1])
        
        ### Cost
        overview_data["Input Cost"].append(measures.iloc[27, 1])
        overview_data["Output Cost"].append(measures.iloc[28, 1])
        overview_data["Total Cost"].append(measures.iloc[29, 1])
        overview_data["Cost per Diagram"].append(measures.iloc[30, 1])
    
    return overview_data
    
def append_averages(overview_data):
    # Loop through each key in the dictionary
    for key in overview_data:
        # Skip the 'setting' key
        if key == "setting":
            overview_data["setting"].append("Avg.")
            continue
        
        if key in ["model", "model diagram", "diagram creation", "examples"]:
            overview_data[key].append("n/a")
            continue
        
        # Calculate the average if the list is not empty
        if overview_data[key]:
            avg_value = sum(overview_data[key]) / len(overview_data[key])
        else:
            avg_value = 0  # Handle case where the list is empty
        
        # Append the average value to the list
        overview_data[key].append(round(avg_value, 3))
    
    # Append "All" to the 'setting' key
    
    
    return overview_data


# Create selection of files to check
settings = [
    # Results file names in "documentation" folder can be listed here    
]




settings[7].split("_")



# Getting Overview Data
overview_data = create_overview_data(settings)

# Calculate Avarege for Relevant information
overview_data_avg = append_averages(overview_data)

# Create overview_df and save as csv
overview_df = pd.DataFrame(overview_data_avg)
overview_df.to_excel("Settings Comparison.xlsx", index=False)