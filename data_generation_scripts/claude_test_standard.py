"""
This script lets you generate data from the Claude models in the STANDARD condition.
You can configure model, temperature, model_runs, and whether to use Chain-of-Thought prompting.
The prompts are generated from the imported test_list.
"""

import anthropic
import random
import csv
import os
from test_list_dict import test_list


client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="api-key-here"
)


condition = "standard"
model_options = ["claude-3-sonnet-20240229", "claude-3-5-sonnet-20240620"]
model = model_options[0]
temperature = 0
model_runs = 10     # number of answers to be collected per question


cot = False     # activate or deactivate the Chain-of-Thought prompt
model_name = f"{model}_cot" if cot else model


def query_function(prompt):
    message = client.messages.create(
        model=model,
        max_tokens=800,
        temperature=temperature,
        messages=[
            {"role": "user", "content": f"{prompt}"}
        ]
    )
    model_response = message.content[0].text
    return model_response


# column headers for the resulting CSV file
claude_data_list = [["model", "q_number", "responses"]]


# iterates through the test_list, creates prompt, prompts model, stores output
for tasks in test_list:
    # the test_list contains the info necessary to create all 20 task prompts
    question_nr = tasks["q_number"]
    task = tasks["task"]

    new_data_entry = [model, question_nr]

    source_tool = tasks["source_tool"]
    object_list = [tasks["afforded_tool"], tasks["associated_tool1"],
                   tasks["associated_tool2"], tasks["irrelevant_tool1"]]

    for i in range(model_runs):         # generate specified number of answers per task question
        random.shuffle(object_list)     # shuffle order of option presentation each time

        normal_prompt = (f"Your task is to {task}. Normally, you would use {source_tool} to accomplish this task. "
                         f"However, {source_tool} is not available to you. At your disposal, you have the objects "
                         f"listed below. Which one of these would you use to accomplish the task? \n"
                         f"{object_list[0]} \n"
                         f"{object_list[1]} \n"
                         f"{object_list[2]} \n"
                         f"{object_list[3]}")

        cot_prompt = f"{normal_prompt} Evaluate each option separately before specifying your choice."

        # status of CoT variable will determine whether normal or CoT prompt is used
        task_prompt = cot_prompt if cot else normal_prompt

        response = query_function(task_prompt)

        # print if you want to see tasks and model answers as they are being generated
        print(f"{task_prompt} \n\n{response}\n\n")

        new_data_entry.append(response)

    claude_data_list.append(new_data_entry)


# view final model output
for element in claude_data_list:
    print(element)


data_folder = '../data'                     # define the path to the data folder
os.makedirs(data_folder, exist_ok=True)     # ensure the data folder exists

# store output in csv in the data folder
filename = os.path.join(data_folder, f"{model_name}_{condition}_raw_data.csv")
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(claude_data_list)

print(f"Data has been written to {filename}")
