"""
This script lets you generate data from the GPT models in the DISTRACTOR condition.
You can configure model, temperature, and model_runs.
The prompts are generated from the imported test_list.
"""

import random
import csv
import os
from openai import OpenAI
from test_list_dict import test_list


client = OpenAI(api_key="your_api_key")


condition = "distractor"
model_options = ["gpt-3.5-turbo", "gpt-4o-2024-08-06"]
model = model_options[0]
temperature = 0
model_runs = 10     # number of answers to be collected per question


def query_function(prompt):
    completion1 = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": f"{prompt}"}
        ],
        max_tokens=800,
        temperature=temperature
    )
    response_afford = completion1.choices[0].message.content
    return response_afford


# column headers for the resulting CSV file
gpt_data_list = [["model", "q_number", "responses"]]


# iterates through the test_list, creates prompt, prompts model, stores output
for tasks in test_list:
    # the test_list contains the info necessary to create all 20 task prompts
    question_nr = tasks["q_number"]
    task = tasks["task"]

    new_data_entry = [model, question_nr]

    source_tool = tasks["source_tool"]
    object_list = [tasks["afforded_tool"], tasks["associated_tool1"],
                   tasks["associated_tool2"], tasks["associated_tool3"],
                   tasks["associated_tool4"], tasks["irrelevant_tool1"],
                   tasks["irrelevant_tool2"], tasks["irrelevant_tool3"],
                   tasks["irrelevant_tool4"]]

    for i in range(model_runs):         # generate specified number of answers per task question
        random.shuffle(object_list)     # shuffle order of option presentation each time

        task_prompt = (f"Your task is to {task}. Normally, you would use {source_tool} to accomplish this task. "
                       f"However, {source_tool} is not available to you. At your disposal, you have the objects "
                       f"listed below. Which one of these would you use to accomplish the task? \n"
                       f"{object_list[0]} \n"
                       f"{object_list[1]} \n"
                       f"{object_list[2]} \n"
                       f"{object_list[3]} \n"    
                       f"{object_list[4]} \n"
                       f"{object_list[5]} \n"
                       f"{object_list[6]} \n"
                       f"{object_list[7]} \n"
                       f"{object_list[8]} \n"
                       f"Evaluate each option separately before specifying your choice.")

        response = query_function(task_prompt)

        # print if you want to see tasks and model answers as they are being generated
        print(f"{task_prompt} \n\n{response}\n\n")

        new_data_entry.append(response)

    gpt_data_list.append(new_data_entry)


# view final model output
for element in gpt_data_list:
    print(element)


data_folder = '../data'                     # define the path to the data folder
os.makedirs(data_folder, exist_ok=True)     # ensure the data folder exists

# store output in csv in the data folder
filename = os.path.join(data_folder, f"{model}_{condition}_raw_data.csv")
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(gpt_data_list)

print(f"Data has been written to {filename}")
