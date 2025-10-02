import pandas as pd
import random
import json
from openai import OpenAI
from pydantic import BaseModel
import numpy as np
import copy
from datetime import datetime
import os
from datetime import date

class NotInRangeError(Exception):
    pass

def load_data(file_path):
    """Load data from an Excel file."""
    return pd.read_excel(file_path)

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, "r") as f:
        return json.load(f)

def load_prompt(prompt_file):
    with open(f"Prompts/{prompt_file}", "r") as f:
        prompt = f.read()
        f.close()
    
    return prompt

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
        
def choose_settings():
    # Defining potential settings to test
    settings = {
        # S1: Model Given = No, Model Created = No, Examples = 0
        "V1.1_woTruth_0Examples_allUserPrompt": {
            "Prompt": "base_prompt.txt",
            "User_Prompt": "prompt_v1.1_woTruth_allUserPrompt.txt",
            "Notes": "prompt_v1.1_woTruth_allUserPrompt_NOTES.txt",
            "Truth": False,
            "Examples": 0,
            "Schema": "response_schema_v0.1.json"
        },

        # S2: Model Given = No, Model Created = No, Examples = 5
        "V1.1_woTruth_5Examples_allUserPrompt": {
            "Prompt": "base_prompt.txt",
            "User_Prompt": "prompt_v1.1_woTruth_allUserPrompt.txt",
            "Notes": "prompt_v1.1_woTruth_allUserPrompt_NOTES.txt",
            "Truth": False,
            "Examples": 5,
            "Schema": "response_schema_v0.1.json"
        },

        # S3: Model Given = No, Model Created = No, Examples = 25
        "V1.1_woTruth_25Examples_allUserPrompt": {
            "Prompt": "base_prompt.txt",
            "User_Prompt": "prompt_v1.1_woTruth_allUserPrompt.txt",
            "Notes": "prompt_v1.1_woTruth_allUserPrompt_NOTES.txt",
            "Truth": False,
            "Examples": 25,
            "Schema": "response_schema_v0.1.json"
        },

        # S4: Model Given = Yes, Model Created = No, Examples = 0
        "V1.1_wTruth_0Examples_allUserPrompt": {
            "Prompt": "base_prompt.txt",
            "User_Prompt": "prompt_v1.1_wTruth_allUserPrompt.txt",
            "Notes": "prompt_v1.1_woTruth_allUserPrompt_NOTES.txt",
            "Truth": True,
            "Examples": 0,
            "Schema": "response_schema_v0.1.json"
        },

        # S5: Model Given = Yes, Model Created = No, Examples = 5
        "V1.1_wTruth_5Examples_allUserPrompt": {
            "Prompt": "base_prompt.txt",
            "User_Prompt": "prompt_v1.1_wTruth_allUserPrompt.txt",
            "Notes": "prompt_v1.1_woTruth_allUserPrompt_NOTES.txt",
            "Truth": True,
            "Examples": 5,
            "Schema": "response_schema_v0.1.json"
        },

        # S6: Model Given = Yes, Model Created = No, Examples = 25
        "V1.1_wTruth_25Examples_allUserPrompt": {
            "Prompt": "base_prompt.txt",
            "User_Prompt": "prompt_v1.1_wTruth_allUserPrompt.txt",
            "Notes": "prompt_v1.1_woTruth_allUserPrompt_NOTES.txt",
            "Truth": True,
            "Examples": 25,
            "Schema": "response_schema_v0.1.json"
        },

        # S7: Model Given = No, Model Created = Yes, Examples = 0
        "V1.1_woTruth_0Examples_allUserPrompt_wDiagramCreation": {
            "Prompt": "base_prompt.txt",
            "User_Prompt": "prompt_v1.1_woTruth_allUserPrompt.txt",
            "Notes": "prompt_v1.1_woTruth_allUserPrompt_NOTES.txt",
            "Truth": False,
            "Examples": 0,
            "Schema": "response_schema_v0.1_wDiagramCreation.json"
        },

        # S8: Model Given = No, Model Created = Yes, Examples = 5
        "V1.1_woTruth_5Examples_allUserPrompt_wDiagramCreation": {
            "Prompt": "base_prompt.txt",
            "User_Prompt": "prompt_v1.1_woTruth_allUserPrompt.txt",
            "Notes": "prompt_v1.1_woTruth_allUserPrompt_NOTES.txt",
            "Truth": False,
            "Examples": 5,
            "Schema": "response_schema_v0.1_wDiagramCreation.json"
        },

        # S9: Model Given = No, Model Created = Yes, Examples = 25
        "V1.1_woTruth_25Examples_allUserPrompt_wDiagramCreation": {
            "Prompt": "base_prompt.txt",
            "User_Prompt": "prompt_v1.1_woTruth_allUserPrompt.txt",
            "Notes": "prompt_v1.1_woTruth_allUserPrompt_NOTES.txt",
            "Truth": False,
            "Examples": 25,
            "Schema": "response_schema_v0.1_wDiagramCreation.json"
        }
    }


    for idx, (key, value) in enumerate(settings.items()):
        print(f"{idx}: {key}")
        
    print()
    while True:
        try: 
            user_choice = input("Please select a setting to test:\n")
            value = int(user_choice)
        
            if value not in range(0, len(settings.items())):
                raise NotInRangeError("Selected number not in range, please try again")
            else:
                print()
                print(f"'{list(settings.items())[value][0]}' was selected")
                print()
                break
            
            
        except NotInRangeError as e:
            print("Error:", str(e))
        except:
            print("Something went wrong, please enter a number...")
            
    return list(settings.items())[value]

def choose_model():
    # ADDED: gpt-5 and gpt-5-mini to the options
    models = ["gpt-5", "gpt-5-mini", "gpt-4o-2024-08-06", "o4-mini-2025-04-16"]

    for idx, model in enumerate(models):
        print(f"{idx}: {model}")
    
    print()
    model_idx = int(input("Please enter the index number of the model you want to choose:\n"))
    model = models[model_idx]
    print()
    return model

def is_reasoning_model(model: str) -> bool:
    # UPDATED: treat GPT-5 family as reasoning models, alongside o1/o3/o4
    return model.startswith(("o1", "o3", "o4", "gpt-5"))

def select_random_responses(student_responses, n=1):
    """Select n random items from student responses."""
    selected_responses = random.sample(list(student_responses.items()), n)
    return dict(selected_responses)

def load_text(text_name):
    with open(f"Texts/{text_name}.txt", "r") as f:
        text = f.read()
        f.close()
    return text

def get_original_text(text_name, model_diagrams):
    text = model_diagrams[text_name]["text"]
    return text

def building_model_diagram(model_diagrams, text_name, setting, response):
    model_diagram = copy.deepcopy(model_diagrams[text_name])
    
    if "text" in model_diagram:
        del model_diagram["text"]

    if setting[1]["Truth"] == False:
        try:
            del model_diagram["Box_1"]["Truth"]
            del model_diagram["Box_2"]["Truth"]
            del model_diagram["Box_3"]["Truth"]  
            del model_diagram["Box_4"]["Truth"]
        except:
            pass

    for row in response.iterrows():
        field = row[1]["Veld"]
        field_number = row[1]["Veldnummer"]
        model_diagram[f"Box_{field_number}"]["Student Response"] = field
        
    return model_diagram

def get_examples(key, filtered_data, setting, text_name, model_diagrams):
    # Creating a df for potential examples to draw (by filtering out the diagrams selected for evaluation)
    example_df = filtered_data[
        (~filtered_data["UUID"].str.contains(key, case=False, na=False, regex=False)) & # this removes the diagram that is currently prepared from the list of potential examples
        (filtered_data["Tekstnaam"]==text_name) # this makes sure that we are only getting examples of the same text as the target diagram
    ]
    
    ## Formatting and selecting n (from settings) examples
    examples_grouped = group_data(example_df)
    example_responses = create_student_responses(examples_grouped)
    selected_examples = select_random_responses(student_responses=example_responses, n=setting[1]["Examples"])

    ## For each selected example, build example input that will be sent to GPT
    input_examples = []
    model_responses = []
    for example_key, selected_response in selected_examples.items():
        
        # Building the example input for the current example
        input_example = building_model_diagram(model_diagrams, text_name, setting, response=selected_response)
        input_examples.append(input_example)
        
        # Building desired response for current example
        ## Loading model response
        model_response = load_json("response.json")
        
        ### Looping through selected response to fill in appropriate input from model response into desired response
        for idx, row in selected_response.iterrows():
            
            ### Getting human code from example
            model_response[f'Box_{row["Veldnummer"]}']['Extraction'] = row["Code"]

            ### Applying Position code to model response
            if row["Code"] == "c":
                model_response[f'Box_{row["Veldnummer"]}']["Position"] = 2
            
            elif row["Veldnummer"] == row["Verbandnummer"]:
                model_response[f'Box_{row["Veldnummer"]}']["Position"] = 1
            
            elif row["Veldnummer"] != row["Verbandnummer"]:
                model_response[f'Box_{row["Veldnummer"]}']["Position"] = 0
            
            else:
                print(f"Something must have gone wrong in extracting the Position of {idx, row}")
            
            ### Applying Correct Position to Model Response
            model_response[f'Box_{row["Veldnummer"]}']["Correct Position"] = row["Verbandnummer"]
            
        for i in range(1, 5):
            if model_response[f"Box_{i}"]["Extraction"] == None:
                model_response[f"Box_{i}"]["Extraction"] = "o"
            
            if model_response[f"Box_{i}"]["Position"] == None:
                model_response[f"Box_{i}"]["Position"] = "9"
            
            if model_response[f"Box_{i}"]["Correct Position"] == None:
                model_response[f"Box_{i}"]["Correct Position"] = "9"

                
        model_responses.append(model_response)

    return input_examples, model_responses

def create_examples_for_prompt(model_inputs, model_responses):
    """This function generates the Exampes that are part of the final promtp"""
    examples = []
    for input_idx, input in enumerate(model_inputs):
        example = f"""## Example {input_idx+1}
        Input:
        {input}
        
        Desired Output:
        {model_responses[input_idx]}
        """
        
        examples.append(example)
        
    prompt_examples = "# Examples" + "\n" + "\n".join(examples)

    return prompt_examples

def prep_batch(system_prompt, user_prompt, response_schema, key, model, reasoning_effort=None):
    """Create the batch request for the current diagram, adapting to reasoning vs standard models."""
    # Base body shared by both models
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": f"{user_prompt}"}
        ],
        "seed": 1234567,              # keep your deterministic setting
        "response_format": response_schema
    }

    if is_reasoning_model(model):
        # Reasoning models: add effort and omit temperature
        body["reasoning_effort"] = reasoning_effort or "medium"
    else:
        # Non-reasoning models: keep your temperature setting
        body["temperature"] = 0

    batch_request = {
        "custom_id": f"request-{key}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": body
    }
    return batch_request


def processing_responses(selected_diagrams):
    """This function puts together the user prompt and calls GPT for each selected diagram"""
    model_diagrams = load_json("model_diagrams.json")
    
    # Defining list to capture batch_requests    
    batch_requests = []
    
    # Looping through selected diagrams to prepare prompt and call on GPT
    for key, response in selected_diagrams.items():
        # Getting original text for current student response
        text_name = key.split("_", 2)[-1]
        text = get_original_text(text_name, model_diagrams)
        
        # Building appropriate diagram structure and filling it with student responses
        model_diagram_with_student_response = building_model_diagram(model_diagrams, text_name, setting, response)

        input_for_prompt = f"#Input\n{model_diagram_with_student_response}"

        
        # Putting tohether user prompt either with or without exampels       
        if setting[1]["Examples"] > 0:
            # Get Model_Inputs and associated Model Responses
            model_inputs, model_responses = get_examples(key=key, filtered_data=filtered_data, setting=setting, text_name=text_name, model_diagrams=model_diagrams)
            
            # Creating Examples for final prompt
            examples_for_prompt = create_examples_for_prompt(model_inputs=model_inputs, model_responses=model_responses)

            if setting[1]["Prompt"] == "base_prompt.txt":
                instructions = load_prompt(setting[1]["User_Prompt"])
                notes = load_prompt(setting[1]["Notes"])
                
                # FIXED: removed stray ' + ' inside string concatenation
                user_prompt = instructions + "\n\n" + f"# Original Text\n{text}\n\n" + input_for_prompt + "\n\n" + examples_for_prompt + "\n\n" + notes
            else:
                user_prompt = f"# Original Text\n{text}\n\n" + input_for_prompt + "\n\n" + examples_for_prompt
        
        else:
            if setting[1]["Prompt"] == "base_prompt.txt":
                instructions = load_prompt(setting[1]["User_Prompt"])
                notes = load_prompt(setting[1]["Notes"])
                
                # FIXED: removed stray ' + ' inside string concatenation
                user_prompt = instructions + "\n\n" + f"# Original Text\n{text}\n\n" + input_for_prompt + "\n\n" + notes
            else:
                user_prompt = f"# Original Text\n{text}\n\n" + input_for_prompt
        
        
        # Creating Batch Request for current response (diagram)
        request = prep_batch(system_prompt, user_prompt, response_schema, key, model, reasoning_effort)
        batch_requests.append(request)
    
    return batch_requests
        
def upload_batch_file(file_name, client):
    
    batch_input_file = client.files.create(
        file=open(f"Batch Input Files/{file_name}.jsonl", "rb"),
        purpose="batch"
    )
    
    return batch_input_file

def order_batch(batch_input_file, client, batch_file_name):
    batch_input_file_id = batch_input_file.id

    batch_request_description = batch_file_name

    batch_info = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
        "description": batch_request_description
        }
    )
    
    return batch_info

# Setting up OpenAI Client
client = OpenAI(
    api_key="",     # paste your OpenAI API key here or set as environmental variable
    project=""      # If you have a specific project defined via the OpenAI Platform or API, you can paste its ID here
)

# Loading data and creating a filtered dataset
file_path = "Data/20220704_student_answers_all_datasets.xlsx" # Exchange with the true path to data here
data_raw = load_data(file_path)
filtered_data = filter_data(data_raw)

# Grouping & randomly selecting student responses based on student-class-text diagram combination
grouped_data = group_data(filtered_data)
student_responses = create_student_responses(grouped_data)

# Get settings to be tested from user
setting = choose_settings()
n = int(input("How many diagrams do you want to evaluate\n"))
model = choose_model()

# Ask for effort whenever a reasoning model is chosen (o-series or gpt-5 family).
reasoning_effort = None
if is_reasoning_model(model):
    _eff = (input("Reasoning effort (low|medium|high) [medium]:\n") or "medium").strip().lower()
    reasoning_effort = _eff if _eff in ("low", "medium", "high") else "medium"

# Selecting correct System Prompt & Response Schema
system_prompt = load_prompt(setting[1]["Prompt"])
response_schema = load_json(setting[1]["Schema"])

# Select a random subset of n diagrams
selected_diagrams = select_random_responses(student_responses, n=n)

# Getting a list of batch requests
batch_requests = processing_responses(selected_diagrams=selected_diagrams)

# Storing the batch requests as a jsonl file
today = date.today()
formatted_date = today.strftime('%Y-%m-%d')

batch_file_name = f"{formatted_date}_{setting[0]}_{model}_n{n}"

with open(f"Batch Input Files/{batch_file_name}.jsonl", "w") as f:
    for request in batch_requests:
        json.dump(request, f)
        f.write("\n")
    
    f.close()

# Uploading Batch File and Creating Batch Order    
upload_choice = input("Do you want to upload the batch file (y/n)?\n")
print()
if upload_choice == "y":
    batch_input_file = upload_batch_file(file_name=batch_file_name, client=client)

order_choice = input("Do you want to order the batch (y/n)?\n")
print()
if order_choice == "y":
    batch_info = order_batch(batch_input_file, client, batch_file_name)