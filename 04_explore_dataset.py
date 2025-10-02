import pandas as pd
import numpy as np

def load_data(file_path):
    """Load data from an Excel file."""
    return pd.read_excel(file_path)

def add_uuid(data):
    data['UUID'] = data['Nummer'].astype(str) + '_' + data['Klas'].astype(str) + '_' + data['Tekstnaam'].astype(str)

    return data

def add_participant_id(data):
    data['PID'] = data['Nummer'].astype(str) + '_' + data['Klas'].astype(str)

    return data
    
def filter_dataset(data):
    """Filter the data based on specific criteria."""
    desar = data[
        (data["Dataset"] == "Desar")
    ]
    
    return desar

def filter_responses(data):
    """Filter the data based on specific criteria."""
    filtered_data = data[
        ((data["Code"] == "g")) | 
        ((data["Code"] == "c")) 
    ]
    
    return filtered_data

def filter_texts(data, text):
    """Filter the data based on specific criteria."""
    filtered_data = data[data["Tekstnaam"] == text]
   
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

def calculate_answer_lengths(data):
    lengths = []
    length_sum = 0
    length_counter = 0


    for idx,  field in enumerate(data["Veld"]):
        field_length = len(str(field).split())
        lengths.append(field_length)
        length_sum += field_length
        length_counter += 1

    average_length = length_sum / length_counter
    sd_length = np.std(lengths)
    
    return min(lengths), max(lengths), average_length, sd_length

# Raw Dataset
data = load_data("") # Paste path to data here
data = add_participant_id(data=data)
data = add_uuid(data=data)
# Dataset filtered for fields that are good or fields that have an error of comission
desar = filter_dataset(data=data)
df_filtered = filter_responses(data=desar)
# Grouping data so that lines of the same diagram belong together
grouped_data = group_data(data=desar)
grouped_data_filtered = group_data(data=df_filtered)

# Grouping
student_responses = create_student_responses(grouped_data)
student_responses_filtered = create_student_responses(grouped_data_filtered)

# Getting overview of filtered and unfiltered data
print("Unfiltered Data:")
print(f"Lines: {len(desar)}")
print(f"Diagrams: {len(grouped_data)}")
print(f"Participants: {len(desar["PID"].unique())}")

print()
print("Filtered Data:")
print(f"Lines: {len(df_filtered)}")
print(f"Diagrams: {len(grouped_data_filtered)}")
print(f"Participants: {len(df_filtered["PID"].unique())}")
print()

# Calculating Answer Length for Unfiltered data
answer_min, answer_max, answer_avg, answer_sd = calculate_answer_lengths(data=df_filtered)
print(f"Overview of Answer Lengts: ({answer_min}, {answer_max}, {round(answer_avg, 3)}, {round(answer_sd, 3)})")
print()

# Getting Measures for Different Texts
texts = ["All", "Beton", "Botox", "Geld", "Metro", "Muziek", "Suez"]

for text in texts: 
    if text == "All":
        df_text = df_filtered
    else:
        df_text = filter_texts(data=df_filtered, text=text)

    good = df_text["Code"].value_counts()["g"]
    commission = df_text["Code"].value_counts()["c"]
    g_c_ratio = good / commission
    print(text)
    
    good_percentage = round((good / (good + commission)) * 100, 1)
    commission_percentage = round((commission / (good + commission)) * 100, 1)
    print(f"g: {good}, {good_percentage}%; c: {commission}, {commission_percentage}%")
    print()