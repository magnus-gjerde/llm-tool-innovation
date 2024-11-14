"""
Automated evaluation script for LLM outputs.

This script loads raw model outputs from a CSV file and uses an OpenAI LLM to evaluate
and convert each answer to a binary (incorrect/correct) data point.
Set the configuration so that it matches the model whose data you want to evaluate.

The program will iterate through each of the chosen model's answers, use the verification model
to compare the individual answers with the correct answer, and then give it a binary
rating of correct or incorrect (0/1).

The binary data is stored in a new csv.
"""

import os
import csv
from openai import OpenAI
from display_text import print_nice


client = OpenAI(api_key="your_api_key")


# select condition
condition_list = ["standard", "distractor", "image"]
condition = condition_list[0]

# select model
model_list = ["gpt-3.5-turbo", "gpt-4o-2024-08-06", "claude-3-sonnet-20240229", "claude-3-5-sonnet-20240620"]
model = model_list[0]

# select if CoT prompting applies
cot = False
model_name = f"{model}_cot" if cot else model


verification_model = "gpt-4o"   # select preffered verification model
temperature = 0


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


# dictionary with the correct answers to the questions
correct_dict = {
    'Q1': 'curtains', 'Q2': 'table tennis racket', 'Q3': 'saucepan', 'Q4': 'swimming cap',
    'Q5': 'ruler', 'Q6': 'kitchen roll', 'Q7': 'wig', 'Q8': 'dvd case', 'Q9': 'beach towel',
    'Q10': 'baseball bat', 'Q11': 'fishing line', 'Q12': 'coffee filter', 'Q13': 'frisbee', 'Q14': 'plasters',
    'Q15': 'apple', 'Q16': 'audio headset', 'Q17': 'one pound coin', 'Q18': 'tennis racket', 'Q19': 'shoelace',
    'Q20': 'picnic blanket'
}

# system prompt to guide the verification model
sys_prompt = ("I am a thorough answer checker. My goal is to read a text output "
              "and decide whether it is correct or incorrect.")


# function to compare test answer with correct answer
def verify_function(response, question_number):
    correct_answer = correct_dict[question_number]  # retrieve relevant correct answer from correct_dict

    verify_prompt = (f"Correct answer: {correct_answer}. \nText output: {response}. \nDid the participant "
                     f"choose the correct answer? Focus on the final and main answer given in the participant's "
                     f"response. If yes, write '1', If no, write '0'. \n"
                     f"Evaluation: ")

    completion1 = client.chat.completions.create(
        model=verification_model,
        messages=[
            {"role": "system", "content": f"{sys_prompt}"},
            {"role": "user", "content": f"{verify_prompt}"}
        ],
        max_tokens=800,
        temperature=temperature
    )
    verification = completion1.choices[0].message.content

    return verification     # the verification output will be 0, 1, or 2


# iterates through the LLM's answers, verifies them with the verify_function, stores the resulting binary data
binary_response_data = []
for question_row in response_list[1:]:      # skip header row
    model, q_number = question_row[:2]      # # extract metadata
    binary_responses = []
    for answer in question_row[2:]:         # iterate through model responses

        print_nice(answer)      # prints the model's answer

        # query the verification model using the specific answer and question number
        model_check = verify_function(answer, q_number)
        print_nice(f"LLM verification: {model_check}")      # print model verification output

        binary_responses.append(int(model_check))

    binary_response_data.append([model, q_number] + binary_responses)


# view the resulting binary data
for row in binary_response_data:
    print(row)


# store the binary data in csv in the data folder
filename = os.path.join(data_folder, f"{model_name}_{condition}_binary_data.csv")
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(binary_response_data)

print(f"Data has been written to {filename}")
