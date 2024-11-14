"""
This script lets you generate data from the GPT models in the IMAGE condition.
You can configure model, temperature, model_runs, and whether to use Chain-of-Thought prompting.
The prompts are generated from the imported test_list.
"""

import csv
import os
import requests
from openai import OpenAI
import random
from test_list_dict import test_list
from encode_images import encode_images_from_folder

client = OpenAI()

# OpenAI API Key
api_key = "your_api_key"


condition = "image"
model_options = ["gpt-4o-2024-08-06"]
model = model_options[0]
temperature = 0
model_runs = 10     # number of answers to be collected per question


cot = False     # activate or deactivate the Chain-of-Thought prompt
model_name = f"{model}_cot" if cot else model


# can be used to verify that the LLM understands the image contents,
# simply replace task_prompt with imrecog_prompt when querying the model
imrecog_prompt = "In brief terms, specify the typical function of the object shown in each of the four images."


# query the model using a text prompt and four images
def image_query(prompt, images):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{images[0]}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{images[1]}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{images[2]}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{images[3]}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 800,
        "temperature": temperature
    }

    img_response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    output = img_response.json()
    answer_text = output['choices'][0]['message']['content']

    return answer_text


# column headers for the resulting CSV file
gpt_data_list = [["model", "q_number", "responses"]]


# iterates through the test_list, creates prompt, prompts model, stores output
for tasks in test_list:
    # the test_list contains the info necessary to create all 20 task prompts
    question_nr = tasks["q_number"]
    task = tasks["task"]
    source_tool = tasks["source_tool"]

    new_data_entry = [model, question_nr]

    # use imported encode_images function to access images in base64 format
    base64_object_images = encode_images_from_folder(question_nr)

    for i in range(model_runs):                 # generate specified number of answers per task question
        random.shuffle(base64_object_images)    # shuffle order of image presentation each time

        normal_prompt = (f"Your task is to {task}. Normally, you would use {source_tool} to accomplish this task. "
                         f"However, {source_tool} is not available to you. At your disposal, you have the objects "
                         f"shown in the four images. Which one of these would you use to accomplish the task?")

        cot_prompt = f"{normal_prompt} Evaluate each option separately before specifying your choice."

        # status of CoT variable will determine whether normal or CoT prompt is used
        task_prompt = cot_prompt if cot else normal_prompt

        response = image_query(task_prompt, base64_object_images)

        # print if you want to see tasks and model answers as they are being generated
        print(f"{task_prompt} \n\n{response}\n\n")

        new_data_entry.append(response)

    gpt_data_list.append(new_data_entry)


# view model output
for element in gpt_data_list:
    print(element)


data_folder = '../data'                     # define the path to the data folder
os.makedirs(data_folder, exist_ok=True)     # ensure the data folder exists

# store output in csv in the data folder
filename = os.path.join(data_folder, f"{model_name}_{condition}_raw_data.csv")
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(gpt_data_list)

print(f"Data has been written to {filename}")
