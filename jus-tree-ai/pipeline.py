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
    01/2025
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
               equpped with an LLM of choice (e.g., LLaMA-3.2). Handles
               CLI args, case processing, decision trees, and results.
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
        # Task-specific setup/files/data.
        self.task = self.args.task
        self.setup_task_files()
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
            help='LLM (e.g., llama3.2).'
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
        raw_output = raw_output.strip()
        # Extract <think></think> content for deepseek-r1 models.
        thought_chain = None
        if 'deepseek-r1' in self.model:
            think_match = re.search(r'<think>(.*?)</think>', raw_output, re.DOTALL)
            if think_match:
                thought_chain = think_match.group(1).strip()
                # Remove the <think></think> content from the raw output.
                raw_output = raw_output.replace(think_match.group(0), '').strip()
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
        # Create the resources to store the experimental results.
        curr_time = datetime.now().strftime('%Y%m%d%H%M%S')
        results_path = f'results/{self.task}/'
        results_file = f'{self.model}-{self.temperature}-{self.args.decision_tree}-{curr_time}.json'
        self.results_path = f'{results_path}{results_file}'

    def build_prompt_llm(self: 'Pipeline', description: str) -> str:
        '''
        Prompt engineering for the LLM. Currently, adjusted for the
        DUO student finance task, but can be easily adapted for other
        tasks by reading the data from some specified prompt files.

            Parameters:
            -------------------------
            description : str
                The description of the case to process.

            Returns:
            -------------------------
            prompt : str
                The prompt for the LLM.
        '''
        # Construct the prompt baseline.
        prompt = f'''
        You are a legal assistant for DUO student finance in the Netherlands.
        Task: Please determine the grant eligibility based on the case description.
        Description: {description}
        '''
        # Include the decision tree - if available.
        if self.args.decision_tree == 'yes':
            # Pre-process the JSON tree into string.
            decision_tree_str = json.dumps(self.decision_tree, indent=4)
            prompt += f'''
        Here is the decision tree in JSON format, based on the law.
        Each node represents the task criterion. Please follow the tree
        logically to derive the decision:\n\n<{decision_tree_str}>\n
        When traversing the tree, follow the logical path you take to decide.
        Example: Age (Eligible) -> Enrollment (NotEligible) -> Decision: "NotEligible".
        '''
        else:
            # Otherwise, specify nodes explicitly to justify LLM's reasoning.
            prompt += '''
        Please analyze the case using these key factors for eligibility:
        - Age
        - Program
        - Enrollment
        - Duration
        - Recognition
        - Nationality
        - HBO_UNI
        - MBO_Under18\n
        Identify the most important node (factor) for your decision.
        '''
        # Specify the output format.
        prompt += '''
        Please provide your answer in the following JSON format. Do NOT include any extra text:
        {
        "prediction": "<Eligible or NotEligible>",'''
        if self.args.decision_tree == 'yes':
            prompt += '"traversal": "<Node1 -> Node2 -> ...>",'
        prompt += '''
        "impact_node": "<The node that most influenced the decision>",
        "reasoning": "<Explanation for your decision in max 2-3 sentences>"
        }'''
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
        prompt = self.build_prompt_llm(description)
        # DEBUG: print the current prompt.
        # print(f'********PROMPT:********\n"{prompt}\n"')
        try:
            # Run the model using via Ollama CLI.
            result = subprocess.run(
                ['ollama', 'run', self.model, prompt],
                capture_output=True,
                text=True
            )
            # DEBUG: print the LLM output.
            print('LLM Output:', result.stdout)
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
        print(f'SUCCESS: The experiments for {self.task} are COMPLETE.\n')

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

    def run(self: 'Pipeline') -> None:
        '''
        Run the full model pipeline; either: experiments or UI version.
        '''
        # TODO: Handle UI version.
        self.process_cases()

if __name__ == '__main__':
    pipe = Pipeline()
    pipe.run()
