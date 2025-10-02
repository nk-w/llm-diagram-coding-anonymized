import pandas as pd
import json
from openai import OpenAI


####################
"""Defining Functions"""

def get_batches(client, limit=25):
    """A function that allows the user to select which batch to download"""
    # Get batches
    print("\n####################\n")
    print("Retrieving Latest Batches:")
    batches = client.batches.list(limit=limit)

    return batches

def batches_by_status(batches):
    # Separate into Active and Completed Batches
    active_batches = []
    complete_batches = []
    failed_batches = []

    for idx, batch in enumerate(batches.data):
        if batch.status == "completed":
            complete_batches.append(batch)
        elif batch.status == "in_progress":
            active_batches.append(batch)
        elif batch.status == "failed":
            failed_batches.append(batch)
        else:
            pass
            
    return active_batches, complete_batches, failed_batches

def get_var_name(var):
    for name, value in locals().items():
        if value is var:
            return name
    return None

def show_batches(batch_list):
    list_name = next(name for name, value in globals().items() if value is batch_list)
    
    # Looping through active batches to disply
    if len(batch_list) > 0:
        print(f"{list_name}:")
        # List active batches
        for idx, batch in enumerate(batch_list):
            print(f"{idx}: {batch.metadata["description"]}:")
            print(f"     Batch ID: {batch.id}")
            print(f"     Status: {batch.status}")
            
        print()
        print()
    else:
        print(f"There are currently no batches in {list_name}\n")

def get_batch_choices():
    batches_to_retrieve = input("Enter the indexs of the batches that you would like to retrieve, separated by a blank space (e.g., 0 3 14):\n")
    print()
    batch_choices_str = batches_to_retrieve.split(" ")
    
    batch_choices = [int(x) for x in batch_choices_str]
    
    return batch_choices

def process_copmpleted_batches(batch_choices):
    for i in batch_choices:
        retrieved_batch = complete_batches[i]
        batch_description = retrieved_batch.metadata["description"]
        file_id = retrieved_batch.output_file_id
        file_response = client.files.content(file_id)
        
        with open(f"Batch Response Files/{batch_description}.jsonl", "w") as f:
            f.write(file_response.text)
        
        responses = []
        for line in file_response.text.splitlines():
            json_line = json.loads(line)
            responses.append(json.loads(json_line["response"]["body"]["choices"][0]["message"]["content"]))


####################
"""Defining required variables and calling functions"""

# Defining OpenAI client
client = OpenAI(
    api_key="",     # paste your OpenAI API key here or set as environmental variable
    project=""      # If you have a specific project defined via the OpenAI Platform or API, you can paste its ID here
)

# Retrieving top n batches and split into active and completed batches
batches = get_batches(client, limit = 25)

"""
for idx, batch in enumerate(batches):
    if idx == 0:
        print(batch.json())
    else:
        continue
"""

active_batches, complete_batches, failed_batches = batches_by_status(batches=batches)

# Give user an overview of all batches
show_batches(batch_list=active_batches)
show_batches(batch_list=failed_batches)
show_batches(batch_list=complete_batches)

# Letting user choose what completed batches to process
if len(complete_batches) > 0:
    batch_choices = get_batch_choices()
    process_copmpleted_batches(batch_choices)

print()
print("All batches processed! Shutting down...\n")
print("####################")
print()