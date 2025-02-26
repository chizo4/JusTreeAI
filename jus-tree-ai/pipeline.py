'''
--------------------------------------------------------------
FILE:
    jus-tree-ai/pipeline.py

INFO:
    This script processes legal decision-making cases using an LLM-based
    pipeline. It evaluates the task eligibility by leveraging decision
    trees and systematic reasoning, e.g., for DUO student finance.

AUTHOR:
    @chizo4 (Filip J. Cierkosz)

VERSION:
    02/2025
--------------------------------------------------------------
'''

import argparse
from datetime import datetime
import json
import os
import re
import subprocess

class Pipeline:
    '''
    -------------------------
    Pipeline - A class for processing cases through the project pipeline
               equipped with an LLM of choice (e.g., LLaMA-3.2). Handles
               CLI args, case processing, decision trees, and results.
               Class mainly designed for experimental part of the project.
    -------------------------
    '''

    def __init__(self: 'Pipeline') -> None:
        '''
        Initialize the Pipeline class.
        '''
        self.args = self.set_args()
        # Model-specific setup.
        self.model = self.args.model
        self.temperature = self.args.temperature
        self.task = self.args.task
        # Set up the results resources (for the current config).
        self.results = []

    def set_args(self: 'Pipeline') -> argparse.Namespace:
        '''
        Parse and handle the CLI arguments.

            Returns:
            -------------------------
            args : argparse.Namespace
                Parsed arguments for the script.
        '''
        parser = argparse.ArgumentParser(description='Data for processing cases.')
        parser.add_argument(
            '--task',
            required=True,
            help='Task (e.g., duo-student-finance).'
        )
        parser.add_argument(
            '--model',
            required=True,
            help='LLM (e.g., llama3.2:3b).'
        )
        parser.add_argument(
            '--decision_tree',
            required=True,
            choices=['yes', 'no'],
            help='Boolean for decision tree.'
        )
        parser.add_argument(
            '--temperature',
            type=float,
            default=0.5,
            help='Temperature for LLM.'
        )
        return parser.parse_args()

    @classmethod
    def load_json(cls, json_path: str) -> list:
        '''
        Helper method to load data from a JSON file.

            Parameters:
            -------------------------
            json_path : str
                The path to the JSON file.

            Returns:
            -------------------------
            data : list
                Parsed JSON data.
        '''
        if not os.path.exists(json_path):
            raise FileNotFoundError(f'File not found: {json_path}')
        with open(json_path, 'r') as f:
            return json.load(f)

    def clean_json(self: 'Pipeline', raw_output: str) -> tuple:
        '''
        Clean up the LLM output to ensure a valid JSON format.

            Parameters:
            -------------------------
            raw_output : str
                The raw text output from the model.

            Returns:
            -------------------------
            cleaned_json : str
                A clean JSON string.
            thought_chain : str or None
                Extracted thoughts if applicable (for deepseek-r1:8b).
        '''
        preprocess_output = raw_output.strip()
        thought_chain = None
        # Handle thoughts for reasoning models.
        if any(model in self.model for model in ['deepseek-r1', 'openthinker']):
            thought_chain, preprocess_output = self.extract_thoughts(raw_output=preprocess_output)
        # Attempt to extract JSON-like content using regex.
        json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
        if json_match:
            return json_match.group(0), thought_chain
        # Handle missing brackets.
        if not raw_output.startswith('{'):
            raw_output = '{' + raw_output
        if not raw_output.endswith('}'):
            raw_output = raw_output + '}'
        cleaned_json = raw_output
        return cleaned_json, thought_chain

    def extract_thoughts(self: 'Pipeline', raw_output: str) -> str:
        '''
        Extract the thought chain from reasoning model (if applicable).
        Also, pre-process the initial output to remove the thought content.

        NOTE: Currently adjusted to handle models from the DeepSeek-R1
              and OpenThinker families.

            Parameters:
            -------------------------
            raw_output : str
                The raw text output from the model.

            Returns:
            -------------------------
            thought_chain : str or None
                Extracted thought content, if available.
            preprocess_output : str
                The pre-processed output without the thoughts tags, etc.
        '''
        thought_chain = None
        if 'deepseek-r1' in self.model:
            match = re.search(r'<think>(.*?)</think>', raw_output, re.DOTALL)
            if match:
                thought_chain = match.group(1).strip()
                preprocess_output = raw_output.replace(match.group(0), '').strip()
        elif 'openthinker' in self.model:
            match = re.search(r'<\|begin_of_thought\|>(.*?)<\|end_of_thought\|>', raw_output, re.DOTALL)
            if match:
                thought_chain = match.group(1).strip()
                preprocess_output = raw_output.replace(match.group(0), '').strip()
                preprocess_output = re.sub(r'<\|begin_of_solution\|>', '', preprocess_output)
                preprocess_output = re.sub(r'<\|end_of_solution\|>', '', preprocess_output)
        return thought_chain, preprocess_output

    def build_prompt_llm(self: 'Pipeline', description: str) -> str:
        '''
        Prompt engineering for the LLM for EXPERIMENTS. The function
        reads the TXT base prompt template and customizes it with
        the task data.

            Parameters:
            -------------------------
            description : str
                The description of the case to process.

            Returns:
            -------------------------
            prompt : str
                The prompt for the LLM.
        '''
        # Construct the prompt customizing the base template.
        prompt = self.prompt_base.replace('{DESCRIPTION}', description)
        # Handle the decision tree inclusion - if available.
        if self.args.decision_tree == 'yes':
            # Parse the decision tree and remove unused tags.
            decision_tree_str = json.dumps(self.decision_tree, indent=4)
            prompt = prompt.replace('{DECISION_TREE_JSON}', decision_tree_str)
            prompt = re.sub(r'<DECISION-TREE-NO>.*?</DECISION-TREE-NO>', '', prompt, flags=re.DOTALL)
            prompt = re.sub(r'</?DECISION-TREE-YES>', '', prompt)
            prompt = re.sub(r'</?TRAVERSAL>', '', prompt)
        else:
            # Otherwise, remove the decision tree JSON and its tags.
            prompt = re.sub(r'<DECISION-TREE-YES>.*?</DECISION-TREE-YES>', '', prompt, flags=re.DOTALL)
            prompt = re.sub(r'</?DECISION-TREE-NO>', '', prompt)
            prompt = re.sub(r'<TRAVERSAL>.*?</TRAVERSAL>', '', prompt, flags=re.DOTALL)
        return prompt

    def process_case_llm(self: 'Pipeline', description: str) -> dict:
        '''
        Process a single case using the target LLM (e.g., LLAMA).

            Parameters:
            -------------------------
            description : str
                The description of the current case to process.

            Returns:
            -------------------------
            output : dict
                The model's decision and reasoning as a JSON object.
        '''
        # Handle prompt engineering - EXPERIMENTS.
        prompt = self.build_prompt_llm(description)
        # DEBUG: print the current prompt.
        # print(f'********PROMPT:********"\n{prompt}\n"')
        try:
            # Run the model using Ollama CLI.
            result = subprocess.run(
                ['ollama', 'run', self.model, prompt],
                capture_output=True,
                text=True
            )
            # DEBUG: print the LLM output.
            # print('LLM Output:', result.stdout)
            # Process the LLM output into JSON.
            clean_output, thought_chain = self.clean_json(result.stdout)
            json_output = json.loads(clean_output)
            if thought_chain:
                json_output['thought_chain'] = thought_chain
            return json_output
        except Exception as e:
            raise RuntimeError(e)

    def process_cases(self: 'Pipeline') -> None:
        '''
        Process all cases via the target LLM and save results.
        '''
        for i, case in enumerate(self.input_cases):
            case_id = case.get('id')
            description = case.get('description')
            print(f'> PROCESS CASE: [{case_id}]\n')
            try:
                # Process the case via LLM.
                output = self.process_case_llm(description)
                case_result = {
                    'case_id': case_id,
                    'prediction': output.get('prediction'),
                    'impact_node': output.get('impact_node'),
                    'reasoning': output.get('reasoning')
                }
                # Include traversal only if used the decision tree.
                if self.args.decision_tree == 'yes':
                    case_result['traversal'] = output.get('traversal')
                # Include thought-chain (if applicable).
                if 'thought_chain' in output:
                    case_result['thought_chain'] = output['thought_chain']
                # Save the JSON results for the current sample.
                case_last = (i == len(self.input_cases) - 1)
                if self.save_results(case_result, case_last):
                    print(f'RESULTS SAVED - CASE: [{case_id}].\n')
                else:
                    print(f'\nWARNING: FAILED TO SAVE RESULTS - CASE: [{case_id}].\n')
            except Exception as e:
                print(f'ERROR for CASE {case_id}: {e}')
        print(f'SUCCESS: The experiments for {self.task} are COMPLETE.\nFILE SAVE: {self.results_path}\n')

    def save_results(self: 'Pipeline', case_result: dict, case_last: bool) -> bool:
        '''
        Save the results to the specified output file.

            Parameters:
            -------------------------
            case_result : dict
                Results for the current case, encoded into dictionary.
            case_last : bool
                Boolean indication of the last case in the batch.

            Returns:
            -------------------------
            bool
                Boolean indication of successful operation for saving the results.
        '''
        try:
            # Check if the file exists and whether is empty.
            file_exists = os.path.exists(self.results_path)
            is_empty = file_exists and os.path.getsize(self.results_path) == 0
            # Open the file (append mode) to add the current result.
            with open(self.results_path, 'a' if file_exists else 'w') as f:
                # Handle a new file.
                if not file_exists or is_empty:
                    f.write('[\n')
                else:
                    f.seek(f.tell() - 2, os.SEEK_SET)
                    f.write(',\n')
                # Append the new case result.
                json.dump(case_result, f, indent=4)
                # Handle the last case in the batch.
                if case_last:
                    f.write('\n]')
            return True
        except (OSError, IOError, json.JSONDecodeError) as e:
            print(f"ERROR: Failed to save case {case_result.get('case_id')}: {e}")
            return False

    def setup_task_files(self: 'Pipeline') -> None:
        '''
        Handle loading ans setting up task-specific files,
        such as: input, output, etc.
        '''
        # Load the input data (cases).
        self.input_file = f'data/{self.task}/cases.json'
        self.input_cases = self.load_json(self.input_file)
        # Handle loading JSON decision tree for the task.
        if self.args.decision_tree == 'yes':
            tree_file = f'data/{self.task}/decision-tree.json'
            self.decision_tree = self.load_json(tree_file)
        # Load the prompt base.
        prompt_file = f'data/{self.task}/prompt-base-pipeline.txt'
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f'Missing prompt template: {prompt_file}')
        with open(prompt_file, 'r') as f:
            self.prompt_base = f.read()
        # Create the resources to store the experimental results.
        curr_time = datetime.now().strftime('%Y%m%d%H%M%S')
        results_path = f'results/{self.task}/'
        results_file = f'{self.model}-{self.temperature}-{self.args.decision_tree}-{curr_time}.json'
        self.results_path = f'{results_path}{results_file}'

    def run(self: 'Pipeline') -> None:
        '''
        Run the full model pipeline for experiments.
        '''
        # Task-specific setup/files/data.
        self.setup_task_files()
        # Run EXPERIMENTS, i.e., process all dataset cases.
        self.process_cases()

if __name__ == '__main__':
    pipe = Pipeline()
    pipe.run()
