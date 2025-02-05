'''
--------------------------------------------------------------
FILE:
    jus-tree-ai/pipeline_agent.py

INFO:
    This script extends the LLM-based pipeline to be used in
    the UI chatbot. It utilizes the best model configuration
    derived based on the experiments, incl. DeepSeek-R1 (8B).

AUTHOR:
    @chizo4 (Filip J. Cierkosz)

VERSION:
    02/2025
--------------------------------------------------------------
'''

import json
from pipeline import Pipeline
import re
import subprocess

class PipelineAgent(Pipeline):
    '''
    -------------------------
    PipelineAgent - Extension of the experimental Pipeline class to be
                  used in the UI chatbot. The pipeline used within this
                  implementation uses the following LLM configuration:
                  * [model]: "deepseek-r1:8b"
                  * [temperature]: 0.8
                  * [decision_tree]: "yes"
    -------------------------
    '''

    TASK = 'duo-student-finance'

    def __init__(self: 'PipelineAgent') -> None:
        '''
        Initialize the class for the agent version of the pipeline.
        '''
        super().__init__()
        # Handle user data in UI mode.
        self.user_data = ''
        self.user_prediction = None
        # Load the task decision tree.
        self.decision_tree = self.load_json(f'data/{self.TASK}/decision-tree.json')

    @classmethod
    def clean_llm_response(cls, raw_response: str) -> str:
        '''
        Clean the raw LLM response by removing the content within <think> tags.
        Function specific for the DeepSeek-R1 models.

            Parameters:
            -------------------------
            raw_response : str
                Raw response from the LLM model.

            Returns:
            -------------------------
            str
                Clean LLM response.
        '''
        clean_response = re.sub(
            r'<think>.*?</think>',
            '',
            raw_response,
            flags=re.DOTALL
        ).strip()
        return clean_response

    def update_user_data(self: 'PipelineAgent', new_user_input: str) -> None:
        self.user_data += f'{new_user_input} '

    def handle_reset_chat_memory(self: 'PipelineAgent', user_input: str) -> bool:
        '''
        Handle resetting the chat memory.

            Parameters:
            -------------------------
            user_input : str
                User input data to process (from UI).

            Returns:
            -------------------------
            bool
                Boolean indication of whether the memory was reset.
        '''
        if user_input.strip().lower() == 'reset':
            self.user_data = ''
            return True
        return False

    def build_prompt_llm(self: 'PipelineAgent') -> None:
        '''
        Construct a structured prompt for the LLM in UI mode.
        Uses self.user_data to dynamically build the case description.

            Returns:
            -------------------------
            prompt : str
                The prompt formatted for the LLM.
        '''
        # Ensure user data is available.
        if not self.user_data.strip():
            return 'No case information provided. Please enter relevant details.'
        # Load the decision tree.
        decision_tree_str = json.dumps(self.decision_tree, indent=4)
        # Engineer the prompt.
        prompt = f'''
        You are an AI assistant assessing DUO student finance eligibility in the Netherlands.

        User Case:
        "{self.user_data.strip()}"

        Decision Rules:
        {decision_tree_str}

        Determine if the user is eligible using these rules.

        Respond in MAX 2 sentences and follow these guidelines:
        1. If eligible, reply: "You are eligible." and briefly explain why.
        2. If not eligible, reply: "Not eligible." and state the key reason.
        3. If unclear, ask for the missing details.

        Do not mention "decision tree" or internal processing in your response.
        Refer to the user as "you". DO NOT answer any unrelated questions!
        '''
        return prompt

    def chat(self: 'PipelineAgent') -> str:
        '''
        Handle the LLM chat mode for the current case.
        '''
        # Engineer the current prompt.
        prompt = self.build_prompt_llm()
        try:
            # Run the model using Ollama CLI.
            result = subprocess.run(
                ['ollama', 'run', self.model, prompt],
                capture_output=True,
                text=True
            )
            response = self.clean_llm_response(raw_response=result.stdout)
            return response
        except Exception as e:
            return None

    def run(self: 'PipelineAgent', user_input=None) -> str:
        '''
        Run the live agent, handling user prompts. Over-writes Pipeline.run().

            Parameters:
            -------------------------
            user_input : str or None
                User input data to process (from UI).
        '''
        if user_input:
            # Listen for resetting chat memory.
            if self.handle_reset_chat_memory(user_input):
                return 'Successfully reset the chat! Please provide new case.'
            else:
                self.update_user_data(user_input)
                llm_answer = self.chat()
                return llm_answer
        return None

if __name__ == '__main__':
    pipe_agent = PipelineAgent()
    pipe_agent.run()
