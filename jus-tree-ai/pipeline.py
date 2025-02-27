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

from datetime import datetime
import json
import os
import re
import subprocess

# Include custom pipeline utils.
from pipeline_utils import PipelineUtils

class Pipeline:
    '''
    -------------------------
    Pipeline - A class for processing cases through the project pipeline
               equipped with an LLM of choice (e.g., LLaMA-3.2). Handles
               case processing, decision trees, etc. Class mainly designed
               for experimental part of the project. Applies PipelineUtils.
    -------------------------
    '''

    # Static log file for LLM output processing.
    LLM_LOG_FILE = './log/llm_output.txt'

    def __init__(self: 'Pipeline') -> None:
        '''
        Initialize the Pipeline class.
        '''
        self.args = PipelineUtils.set_args()
        # Model-specific setup.
        self.model = self.args.model
        self.temperature = self.args.temperature
        self.task = self.args.task
        # Set up the results resources (for the current config).
        self.results = []

    def setup_task_files(self: 'Pipeline') -> None:
        '''
        Handle loading ans setting up task-specific files,
        such as: input, output, etc.
        '''
        # Load the input data (cases).
        self.input_file = f'data/{self.task}/cases.json'
        self.input_cases = PipelineUtils.load_json(self.input_file)
        # Handle loading JSON decision tree for the task.
        if self.args.decision_tree == 'yes':
            tree_file = f'data/{self.task}/decision-tree.json'
            self.decision_tree = PipelineUtils.load_json(tree_file)
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
        # Initialize the LLM output LOG file and reset its content.
        os.makedirs(os.path.dirname(self.LLM_LOG_FILE), exist_ok=True)
        open(self.LLM_LOG_FILE, 'w').close()

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

    def ollama_llm(self: 'Pipeline', prompt: str) -> None:
        '''
        Run the model using Ollama CLI. Stream output into TXT log file.

            Parameters:
            -------------------------
            prompt : str
                The prompt for the LLM.
        '''
        with open(self.LLM_LOG_FILE, 'w') as f:
            # Run Ollama CLI.
            process = subprocess.Popen(
                ['ollama', 'run', self.model, prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Stream output line-by-line to the log file. Avoid truncation issues.
            full_output = []
            for line in iter(process.stdout.readline, ''):
                f.write(line)
                f.flush()
                full_output.append(line.strip())

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
        # Reset the log file for each case.
        open(self.LLM_LOG_FILE, 'w').close()
        # Handle prompt engineering - EXPERIMENTS.
        prompt = self.build_prompt_llm(description)
        # DEBUG: print the current prompt.
        # print(f'********PROMPT:********"\n{prompt}\n"')
        try:
            # Run the model using Ollama CLI and stream its output.
            self.ollama_llm(prompt=prompt)
            # Read back LLM output from TXT and clean results.
            json_output = PipelineUtils.build_llm_result_json(
                log_file=self.LLM_LOG_FILE,
                model=self.model
            )
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
                if PipelineUtils.save_results(self.results_path, case_result, case_last):
                    print(f'RESULTS SAVED - CASE: [{case_id}].\n')
                else:
                    print(f'\nWARNING: FAILED TO SAVE RESULTS - CASE: [{case_id}].\n')
            except Exception as e:
                print(f'ERROR for CASE {case_id}: {e}')
        print(f'SUCCESS: The experiments for {self.task} are COMPLETE.\nFILE SAVE: {self.results_path}\n')

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
