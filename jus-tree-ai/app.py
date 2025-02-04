'''
--------------------------------------------------------------
FILE:
    jus-tree-ai/app.py

INFO:
    This script runs the demo app for the JusTreeAI chatbot.

AUTHOR:
    - @chizo4 (Filip J. Cierkosz)
    - Eduard Cruset

VERSION:
    02/2025
--------------------------------------------------------------
'''

from flask import Flask, render_template, request, jsonify
import re
from typing import List

# Import the JusTreeAI pipeline.
from pipeline import Pipeline

# Config for Flask app.
app = Flask(__name__, template_folder='ui', static_folder='ui/static')

def clean_user_prompt(user_prompt: List[str]) -> str:
    '''
    Simple clean-up for user prompt(s) by removing unwanted characters.
    '''
    user_prompt = ' '.join(user_prompt).strip()
    user_prompt = re.sub(r'[^\x20-\x7E]', '', user_prompt)
    user_prompt = re.sub(r'\s+', ' ', user_prompt)
    user_prompt = re.sub(r'<.*?>', '', user_prompt)
    user_prompt = re.sub(r'[^\w\s,.!?-]', '', user_prompt)
    return user_prompt

def chat_with_llm_bot(raw_user_prompt: List[str]) -> str:
    '''
    Handle chat by integrating LLM Pipeline with UI.
    '''
    user_prompt = clean_user_prompt(user_prompt=raw_user_prompt)
    # Handle empty input after sanitization.
    if not user_prompt:
        return 'INVALID PROMPT: Please try again!'
    # LLM THINKING...
    pipe.run(user_prompt)
    llm_answer = pipe.llm_answer.strip()
    # Handle no/wrong response from LLM.
    if not llm_answer:
        return 'ERROR: Please try again!'
    return llm_answer

@app.route('/')
def home():
    '''
    Handle the demo page.
    '''
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    '''
    Handle the chat request from the user.
    '''
    user_message = request.json['message']
    bot_response = chat_with_llm_bot([user_message])
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    # Run the app and initialize the pipeline instance.
    pipe = Pipeline()
    app.run(debug=True)
