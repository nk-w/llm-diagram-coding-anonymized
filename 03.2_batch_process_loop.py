import json
import os
import glob
import pandas as pd

"""Defining Functions"""


def load_batch_responses(file_name):
    """A function that loads a specific batch response file and returns the llm response & used tokens"""
    # Creating array to capture each response (one per line)
    responses = {}
    input_tokens = []
    output_tokens = []
    
    # Loading jsonl response file and looping through lines to add to responses array
    with open(f"Batch Response Files/{file_name}", "r") as f:
        for line in f:
            json_line = json.loads(line)

            key = json_line["custom_id"].replace("request-", "")
            value = json.loads(json_line["response"]["body"]["choices"][0]["message"]["content"])
            
            input_token = json_line["response"]["body"]["usage"]["prompt_tokens"]
            output_token = json_line["response"]["body"]["usage"]["completion_tokens"]
            
            responses[key] = value
            
            input_tokens.append(input_token)
            output_tokens.append(output_token)
    
    return responses, input_tokens, output_tokens

def token_sum(tokens):
    """A function summing the tokens retrieved from the load_batch_responses function"""
    # Setting up token sum counter
    summed_tokens = 0
    
    # Looping through array of tokens derived from load_batch_function and adding each to summed_tokens counter
    for token in tokens:
        summed_tokens += token
        
    return summed_tokens

def cost_calc(input, output, model):
    """A function calculating the costs of the diagram analysis based on the model that was used"""
    # Defining model costs based on https://openai.com/api/pricing/
    models = {
        "gpt-4o-2024-08-06": {
            "input cost": 1.25,
            "output cost": 5
        },
        "o4-mini-2025-04-16": {
            "input cost": 0.55,
            "output cost": 2.2
        },
        "gpt-5": {
            "input cost": 0.625,
            "output cost": 5
        },
        "gpt-5-mini": {
            "input cost": 0.125,
            "output cost": 1
        }
    }
    
    # Calculating costs by applying costs per 1M tokens
    input_costs = models[model]["input cost"] * (input / 1000000)
    output_costs = models[model]["output cost"] * (output / 1000000)
    total_costs = input_costs + output_costs
    
    return input_costs, output_costs, total_costs

def load_data(file_path="Data/20220704_student_answers_all_datasets.xlsx"): # Set path to data here
    """Load data from an Excel file."""
    return pd.read_excel(file_path)

def filter_data(data):
    """Filter the data based on specific criteria."""
    filtered_data = data[
        ((data["Dataset"] == "Desar") & (data["Code"] == "g")) | 
        ((data["Dataset"] == "Desar") & (data["Code"] == "c")) 
    ]

    filtered_data['UUID'] = filtered_data['Nummer'].astype(str) + '_' + filtered_data['Klas'].astype(str) + '_' + filtered_data['Tekstnaam'].astype(str)
    
    return filtered_data

def group_data(data):
    """Group data by 'Nummer', 'Klas', and 'Tekstnaam'."""
    return data.groupby(["Nummer", "Klas", "Tekstnaam"])

def create_student_responses(grouped_data):
    """Create a dictionary of student responses."""
    # Defining empty student response object. 
    student_responses = {}
    
    # Looping through grouped data to fill student_responses
    for (Nummer, Klas, Tekstnaam), group in grouped_data:
        # Setting unique ID, Class, and Text combination as Key
        student_text_key = f"{Nummer}_{Klas}_{Tekstnaam}"
        # Saving Group as value in student_response
        student_responses[student_text_key] = group
    
    return student_responses

def calculating_confusion_matrix(row, Code_Field, LLM_Code_Field, Agreement_Field, ConMat_Field, Correct, Incorrect):
    if row[Code_Field] == Correct and row[LLM_Code_Field] == Correct:
        row[Agreement_Field] = 1
        row[ConMat_Field] = "TP"
    elif row[Code_Field] == Correct and row[LLM_Code_Field] == Incorrect:
        row[Agreement_Field] = 0
        row[ConMat_Field] = "FN"
    elif row[Code_Field] == Incorrect and row[LLM_Code_Field] == Correct:
        row[Agreement_Field] = 0
        row[ConMat_Field] = "FP"
    elif row[Code_Field] == Incorrect and row[LLM_Code_Field] == Incorrect:
        row[Agreement_Field] = 1
        row[ConMat_Field] = "TN"

def creating_comparison_df(responses, student_responses):
    # Setting up rows to capture each row with original response and llm coding
    rows = []

    # Looping through llm responses to attach the llm coding to the right row 
    for key, value in responses.items():
        # Determining correct original responses for current llm coding
        original_response = student_responses[key]
        llm_response = value

        # Looping through the rows of the current response to add the llm coding to the right field (i.e., row)
        for row in original_response.iterrows():
            content = row[1]
            field_number = content["Veldnummer"]
            
            content["LLM_Code"] = llm_response[f"Box_{field_number}"]["Extraction"]
            content["LLM_PositionCode"] = llm_response[f"Box_{field_number}"]["Position"]
            content["LLM_CorrectPosition"] = llm_response[f"Box_{field_number}"]["Correct Position"]
            rows.append(content)
    
    for row in rows:
        # Adding columns for agreement (0, 1) and response categorisation (TP, TN, FP, FN)
        calculating_confusion_matrix(row=row, Code_Field="Code", LLM_Code_Field="LLM_Code", Agreement_Field="Extraction Agreement", ConMat_Field="Extraction ConMat", Correct="g", Incorrect="c")
        
        # Adding columns for Position to compare coding between 
        ## Adding PositionCode clolumn with boolean whether Veldnummer & Verbandnummer match
        if row["Code"] == "c":
            row["PositionCode"] = 2
        elif row["Veldnummer"] == row["Verbandnummer"]:
            row["PositionCode"] = 1
        else:
            row["PositionCode"] = 0
        
        ## Adding position Code Agreement
        calculating_confusion_matrix(row=row, Code_Field="PositionCode", LLM_Code_Field="LLM_PositionCode", Agreement_Field="PositionCode Agreement", ConMat_Field="PositionCode ConMat", Correct=1, Incorrect=0)
        
        ## Adding CorrectPosition Agreemant
        if row["Verbandnummer"] == row["LLM_CorrectPosition"]:
            row["Position Agreement"] = 1
        else:
            row["Position Agreement"] = 0
        
    return pd.DataFrame(rows) 

def calculating_measures(comparison_df, ConMat_Field):
    # Calculating Measures for Extraction
    ## Getting Counts for Confusion Matrix
    TP = comparison_df[ConMat_Field].value_counts().get("TP", 0)
    FN = comparison_df[ConMat_Field].value_counts().get("FN", 0)
    FP = comparison_df[ConMat_Field].value_counts().get("FP", 0)
    TN = comparison_df[ConMat_Field].value_counts().get("TN", 0)
    
    ## Calculating Kappa
    ### Calculating observed and expeted proportions
    p_o = (TP+TN)/(TP+FN+FP+TN) if (TP+FN+FP+TN) != 0 else 0

    p_true = ((TP+FN)/(TP+FN+FP+TN))*((TP+FP)/(TP+FN+FP+TN)) if (TP+FN+FP+TN) != 0 else 0
    p_false = ((FP+TN)/(TP+FN+FP+TN))*((FN+TN)/(TP+FN+FP+TN)) if (TP+FN+FP+TN) != 0 else 0
    p_e = p_true + p_false

    k = (p_o-p_e)/(1-p_e) if (1-p_e) != 0 else 0

    ## Calculating Accuracy
    Acc = (TP+TN)/(TP+FN+FP+TN) if (TP+FN+FP+TN) != 0 else 0
    
    ## Calculating Precision
    Prec = (TP)/(TP+FP) if (TP+FP) != 0 else 0
    
    ## Calculating Recall
    Rec = (TP)/(TP+FN) if (TP+FN) != 0 else 0
    
    ## Calculating F_1
    F_1 = (2*(Prec*Rec))/(Prec+Rec) if (Prec+Rec) != 0 else 0
    
    return k, Acc, Prec, Rec, F_1, TP, FN, FP, TN


"""Executing Code (batch over folder)"""

# Discover all .jsonl files in the batch folder
BATCH_DIR = "Batch Response Files"
jsonl_paths = sorted(glob.glob(os.path.join(BATCH_DIR, "*.jsonl")))

# Ensure output directory exists
os.makedirs("documentation", exist_ok=True)

# Load and prepare the original dataset once (shared across files)
data = load_data()
filtered_data = filter_data(data)
grouped_data = group_data(data=filtered_data)
student_responses = create_student_responses(grouped_data=grouped_data)

if not jsonl_paths:
    print(f"No .jsonl files found in '{BATCH_DIR}'. Nothing to process.")
else:
    for jsonl_path in jsonl_paths:
        file_name = os.path.basename(jsonl_path)
        print(f"Processing: {file_name}")

        # Extract model name and number of diagrams from file name
        llm_model = file_name.split("_")[-2:][0]
        n_diagrams = int(file_name.split("_")[-1:][0].replace(".jsonl", "").replace("n", ""))

        # Get Batch Responses & tokens
        responses, input_tokens, output_tokens = load_batch_responses(file_name)

        # Calculating Costs
        summed_input_tokens = token_sum(tokens=input_tokens)
        summed_output_tokens = token_sum(tokens=output_tokens)
        input_costs, output_costs, total_costs = cost_calc(input=summed_input_tokens, output=summed_output_tokens, model=llm_model)

        # Integrating original student responses with llm codings
        comparison_df = creating_comparison_df(responses, student_responses)

        # Calculating Measures
        ## For Extraction
        Kappa_Ext, Accuracy_Ext, Precision_Ext, Recall_Ext, F_1_Ext, TP_Ext, FN_Ext, FP_Ext, TN_Ext = calculating_measures(comparison_df=comparison_df, ConMat_Field="Extraction ConMat")

        ## For Position
        ### filtering Comparison DF to only include rows where human and AI agreed that extraction was correct
        position_DF = comparison_df[
            (comparison_df["Code"] == "g") &
            (comparison_df["Extraction Agreement"] == 1)
        ]

        ### Calculating Measures (kept exactly as in your original code)
        Kappa_Pos, Accuracy_Pos, Precision_Pos, Recall_Pos, F_1_Pos, TP_Pos, FN_Pos, FP_Pos, TN_Pos = calculating_measures(comparison_df=comparison_df, ConMat_Field="PositionCode ConMat")

        # Preparing Measures DF to write it to documentation file
        measures_data = [
            ("EXTRACTION DATA", ""),
            ("Accuracy", round(Accuracy_Ext, 3)),
            ("F_1", round(F_1_Ext, 3)),
            ("Precision", round(Precision_Ext, 3)),
            ("Recall", round(Recall_Ext, 3)),
            ("ROC AUC", "N/A"),
            ("Kappa H-H", "N/A"),
            ("Kappa H-M", round(Kappa_Ext, 3)),
            ("TP", TP_Ext),
            ("FN", FN_Ext),
            ("FP", FP_Ext),
            ("TN", TN_Ext),
            ("", ""),
            ("POSITION DATA", ""),
            ("Accuracy", round(Accuracy_Pos, 3)),
            ("F_1", round(F_1_Pos, 3)),
            ("Precision", round(Precision_Pos, 3)),
            ("Recall", round(Recall_Pos, 3)),
            ("ROC AUC", "N/A"),
            ("Kappa H-H", "N/A"),
            ("Kappa H-M", round(Kappa_Pos, 3)),
            ("TP", TP_Pos),
            ("FN", FN_Pos),
            ("FP", FP_Pos),
            ("TN", TN_Pos),
            ("", ""),
            ("COSTS", ""),
            ("Input", round(input_costs, 3)),
            ("Output", round(output_costs, 3)),
            ("Total", round(total_costs, 3)),
            ("Per Diagram", round(total_costs / n_diagrams, 4))
        ]

        # Create a DataFrame from the list of tuples
        measures_df = pd.DataFrame(measures_data, columns=["Measure", "Value"])

        # Reorder comparison_df for more logical variable order
        comparison_df = comparison_df[[
            "Dataset", "UUID", "Veld", "Code", "LLM_Code", "Extraction Agreement", "Extraction ConMat",
            "Veldnummer", "Verbandnummer", "PositionCode", "LLM_PositionCode", "LLM_CorrectPosition",
            "PositionCode Agreement","PositionCode ConMat", "Position Agreement"
        ]]

        # Write outputs per file
        output_path = os.path.join("documentation", f"{file_name}.xlsx")
        with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
            measures_df.to_excel(writer, sheet_name="Measures", index=False)
            comparison_df.to_excel(writer, sheet_name="Data", index=False)
            
            workbook = writer.book
            measures_sheet = writer.sheets["Measures"]
            data_sheet = writer.sheets["Data"]
            
            measures_sheet.autofit()
            data_sheet.autofit()
            data_sheet.set_column("C:C", 80)

        print(f"Wrote: {output_path}")
