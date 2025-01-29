'''
--------------------------------------------------------------
FILE:
    jus-tree-ai/pipeline.py

INFO:
    TODO

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

    def setup_prompt_llm(self: 'Pipeline', description: str) -> str:
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
        print('prompt construction!')
        # Construct the prompt baseline.
        prompt = f'''
        You are a legal reasoning assistant for DUO student finance in the Netherlands.
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
        }
        '''
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
        prompt = self.setup_prompt_llm(description)
        print(prompt)
        # try:
        #     # TODO: proper params passed into LLM here.
        #     # Run the model using via Ollama CLI.
        #     result = subprocess.run(
        #         ['ollama', 'run', self.model, prompt],
        #         # ['ollama', 'run', self.model, '--temperature', str(self.args.temperature), prompt],
        #         capture_output=True,
        #         text=True
        #     )
        #     print("Command Output:", result.stdout)  # Debug: Print model output
        #     return json.loads(result.stdout.strip())
        # except Exception as e:
        #     raise RuntimeError(e)

    def process_cases(self: 'Pipeline') -> None:
        '''
        Process all cases via the target LLM.
        '''
        for case in self.input_cases:
            case_id = case.get('id')
            description = case.get('description')
            print(f'> PROCESS CASE: [{case_id}]\n')
            try:
                self.process_case_llm(description)
                # output = self.process_case_llm(description)
                # TODO: what to store?
                # self.results.append({
                #     'case_id': case_id
                #     # 'decision': output.get('decision'),
                #     # 'reasoning': output.get('reasoning')
                # })
            except Exception as e:
                print(f'ERROR for CASE {case_id}: {e}')

    def save_results(self: 'Pipeline') -> None:
        '''
        Save the results to the specified output file.
        '''
        with open(self.results_path, 'w') as outfile:
            json.dump(self.results, outfile, indent=4)
        print(f'RESULTS SAVED: "{self.results_path}".')

    def run(self: 'Pipeline') -> None:
        '''
        Run the full model pipeline - process cases, and save results.
        '''
        self.process_cases()
        # self.save_results()

if __name__ == '__main__':
    pipe = Pipeline()
    pipe.run()
