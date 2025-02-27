'''
--------------------------------------------------------------
FILE:
    jus-tree-ai/pipeline_utils.py

INFO:
    Utility class to handle pipeline-related tasks, such as:
    CLI args, JSON processing, file loading, etc.

AUTHOR:
    @chizo4 (Filip J. Cierkosz)

VERSION:
    02/2025
--------------------------------------------------------------
'''

import argparse
import os
import json
import re

class PipelineUtils:
    '''
    -------------------------
    PipelineUtils - A utility class for handling JSON processing, file
                    loading, and output extraction.
    -------------------------
    '''

    @staticmethod
    def set_args() -> argparse.Namespace:
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

    @staticmethod
    def load_json(json_path: str) -> list:
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

    @staticmethod
    def clean_json(raw_output: str, model: str) -> tuple:
        '''
        Clean up the LLM output to ensure a valid JSON format.

            Parameters:
            -------------------------
            raw_output : str
                The raw text output from the model.
            model : str
                Current model name (LLM).

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
        if any(model in model for model in ['deepseek-r1', 'openthinker']):
            thought_chain, preprocess_output = PipelineUtils.extract_thoughts(
                raw_output=preprocess_output,
                model=model
            )
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

    @staticmethod
    def extract_thoughts(raw_output: str, model: str) -> tuple:
        '''
        Extract the thought chain from reasoning model (if applicable).
        Also, pre-process the initial output to remove the thought content.

        NOTE: Currently adjusted to handle models from the DeepSeek-R1
              and OpenThinker families.

            Parameters:
            -------------------------
            raw_output : str
                The raw text output from the model.
            model : str
                Current model name (LLM).

            Returns:
            -------------------------
            thought_chain : str or None
                Extracted thought content, if available.
            preprocess_output : str
                The pre-processed output without the thoughts tags, etc.
        '''
        thought_chain = None
        preprocess_output = raw_output.strip()
        if 'deepseek-r1' in model:
            match = re.search(r'<think>(.*?)</think>', raw_output, re.DOTALL)
            if match:
                thought_chain = match.group(1).strip()
                preprocess_output = raw_output.replace(match.group(0), '').strip()
        elif 'openthinker' in model:
            match = re.search(r'<\|begin_of_thought\|>(.*?)<\|end_of_thought\|>', raw_output, re.DOTALL)
            if match:
                thought_chain = match.group(1).strip()
                preprocess_output = raw_output.replace(match.group(0), '').strip()
                preprocess_output = re.sub(r'<\|begin_of_solution\|>', '', preprocess_output)
                preprocess_output = re.sub(r'<\|end_of_solution\|>', '', preprocess_output)
            else:
                # Check if the thought chain is too long to be processed...
                if '<|begin_of_thought|>' in raw_output:
                    print('WARNING: Openthinker output is too long to be processed.')
                    thought_chain = None
        return thought_chain, preprocess_output

    @staticmethod
    def save_results(results_path: str, case_result: dict, case_last: bool) -> bool:
        '''
        Save the results to the specified output file.

            Parameters:
            -------------------------
            results_path : str
                The path to the output results.
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
            file_exists = os.path.exists(results_path)
            is_empty = file_exists and os.path.getsize(results_path) == 0
            # Open the file (append mode) to add the current result.
            with open(results_path, 'a' if file_exists else 'w') as f:
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
