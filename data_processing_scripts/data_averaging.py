"""
Data averaging script for LLM binary data.

This script, taking binary LLM data as input, will compute two types of averages.
1. It will compute model_run averages: average correct per round of answers (columns).
2. It will compute question averages: average correct per individual question (rows).

Set the configuration so that it matches the model whose data you want to process.

The average data are stored as two new csv files, one containing model_run averages,
the other containing question averages.
"""

import os
import pandas as pd


# select condition
condition_list = ["standard", "distractor", "image"]
condition = condition_list[0]

# select model
model_list = ["gpt-3.5-turbo", "gpt-4o-2024-08-06", "claude-3-sonnet-20240229", "claude-3-5-sonnet-20240620"]
model = model_list[0]

# select if CoT prompting applies
cot = False
model_name = f"{model}_cot" if cot else model


# load the CSV file with the binary data from the data folder
data_folder = '../data'     # define the path to the data folder
file_path = os.path.join(data_folder, f"{model_name}_{condition}_binary_data.csv")


def process_binary_data(file_path, model_name, condition):
    """
    This function takes raw binary data (1s and 0s) representing model responses across multiple
    runs and questions, and computes:
    1. Average accuracy per model run
    2. Average accuracy per question
    3. Overall average accuracy

    Parameters:
    -----------
    file_path : str
        Path to the input CSV containing binary response data
    model_name : str
        Name of the language model (e.g., 'gpt-3.5-turbo')
    condition : str
        Experimental condition (e.g., 'standard', 'distractor')

    Returns:
    --------
    tuple(DataFrame, DataFrame)
        Two dataframes containing run averages and question averages respectively
    """
    # read input data and create model run column headers
    df = pd.read_csv(file_path, header=None)
    df.columns = ['model', 'q_number'] + [f'run_{i + 1}' for i in range(len(df.columns) - 2)]

    print("\nFirst few rows of data:")
    print(df.head())

    # compute and format averages by model_runs
    run_averages = df.iloc[:, 2:].mean()
    runs_df = pd.DataFrame({
        'model_run': [f'{model_name}_run{i + 1}' for i in range(len(run_averages))],
        'model': model_name,
        'condition': condition,
        'average_correct': run_averages.round(2)
    })

    # compute and format averages by question
    question_averages = df.iloc[:, 2:].mean(axis=1)
    questions_df = pd.DataFrame({
        'q_number': df['q_number'],
        'model': model_name,
        'condition': condition,
        'average_correct': question_averages.round(2)
    })

    # define output paths
    runs_output = os.path.join(data_folder, f'{model_name}_{condition}_data_by_run.csv')
    questions_output = os.path.join(data_folder, f'{model_name}_{condition}_data_by_q.csv')

    # save results to CSV files
    runs_df.to_csv(runs_output, index=False)
    questions_df.to_csv(questions_output, index=False)

    # calculate and display total average accuracy
    total_avg = df.iloc[:, 2:].values.mean().round(2)
    print(f"Total average score: {total_avg}")

    return runs_df, questions_df


run_averages, question_averages = process_binary_data(file_path, model_name, condition)
