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

from pipeline import Pipeline

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

    def __init__(self: 'PipelineAgent') -> None:
        '''
        Initialize the class for the agent version of the pipeline.
        '''
        super().__init__()
        # Handle user data in UI mode.
        self.user_data = ''
        self.user_prediction = None

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

    def chat(self: 'PipelineAgent', user_input=None) -> str:
        '''
        Handle the LLM chat mode for the current case.
        '''
        # Listen for resetting chat memory.
        if user_input and self.handle_reset_chat_memory(user_input):
            return 'Successfully reset the chat! Please provide new case.'
        # PSEUDO-CODE:
        # #1: Engineer the current prompt - tune `build_prompt_llm`.
        # #2: Above triggered by `process_case_llm`, so just receive results.
        # #3: Scrape useful fields from JSON output.
        # #4: return user-friendly response.
        # (#5: adjust waiting time in UI)
        return 'random data'

    def run(self: 'PipelineAgent', user_input=None) -> str:
        '''
        Run the live agent, handling user prompts.

            Parameters:
            -------------------------
            user_input : str or None
                User input data to process (from UI).
        '''
        if user_input:
            llm_answer = self.chat(user_input)
            return llm_answer
        return None

if __name__ == '__main__':
    pipe_agent = PipelineAgent()
    pipe_agent.run()
