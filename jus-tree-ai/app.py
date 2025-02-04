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
from typing import List
import os

# Import the JusTreeAI pipeline.
from pipeline import Pipeline

# Config for Flask app.
app = Flask(__name__, template_folder='ui', static_folder='ui/static')

# Your chatbot function
def get_response_from_bot(user_prompt: List[str]) -> str:
    user_prompt = ' '.join(user_prompt)
    print(f'\n{user_prompt}\n')
    return 'Random answer.'

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
    bot_response = get_response_from_bot([user_message])
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    # Run the app and initialize the pipeline instance.
    pipe = Pipeline()
    app.run(debug=True)
