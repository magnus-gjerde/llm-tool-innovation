"""
Manual evaluation script for LLM outputs.

This script loads raw model outputs from a CSV file and facilitates manual binary
evaluation (correct/incorrect) of each answer. Set the configuration so that it
matches the model whose data you want to evaluate.

Key features:
- Loads raw output data for a specific model and condition
- Presents each answer for manual evaluation
- Uses 1 (correct) and 3 (incorrect) keys for ergonomic input
- Stores binary evaluation results in a new CSV file

Note: The 3 key is used instead of 0 for incorrect responses due to keyboard
ergonomics, and is automatically converted to 0 in the stored data.
"""

import csv
import os
from display_text import print_nice


# select condition
condition_list = ["standard", "distractor", "image"]
condition = condition_list[0]

# select model
model_list = ["gpt-3.5-turbo", "gpt-4o-2024-08-06", "claude-3-sonnet-20240229", "claude-3-5-sonnet-20240620"]
model = model_list[0]

# select if CoT prompting applies
cot = False
model_name = f"{model}_cot" if cot else model


# load the CSV file with the raw output data from the data folder
data_folder = '../data'     # define the path to the data folder
file_path = os.path.join(data_folder, f"{model_name}_{condition}_raw_data.csv")

# store the imported raw data as a list of lists
with open(file_path, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    response_list = list(csv_reader)

# inspect the raw data list
for row in response_list:
    print(row)


# iterates through the LLM's answers, ask you to check and rate them, stores the resulting binary data
binary_response_data = []
for question_row in response_list[1:]:       # skip header row
    model, q_number = question_row[:2]       # extract metadata
    binary_responses = []
    for answer in question_row[2:]:          # iterate through model responses
        print_nice(answer)

        # get evaluator input (1=correct, 3=incorrect for ergonomic typing)
        binary_evaluation = input("Correct or incorrect? ")

        # validation loop ensures only valid inputs (1 or 3) are accepted
        while not (binary_evaluation == "3" or binary_evaluation == "1"):
            binary_evaluation = input("Correct or incorrect? ")

        if binary_evaluation == "3":    # convert the 3 back to 0
            binary_evaluation = "0"

        binary_responses.append(int(binary_evaluation))

    binary_response_data.append([model, q_number] + binary_responses)


# view the binary resulting data
for row in binary_response_data:
    print(row)


# store the binary data in csv in the data folder
filename = os.path.join(data_folder, f"{model_name}_{condition}_binary_data.csv")
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(binary_response_data)

print(f"Data has been written to {filename}")
