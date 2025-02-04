from flask import Flask, render_template, request, jsonify
from typing import List
import os

# Import the JusTreeAI pipeline.
from pipeline import Pipeline

# Config for Flask app.
app = Flask(__name__, template_folder='ui', static_folder='ui/static')

# Your chatbot function
def get_response_from_bot(input: List[str]) -> str:

    if input[0] == "Hello":
        return "Hi! How can I help you?"

    # I would like to request information on whether I am elegible for the student finance:
    if "I would like" in input[0]:
        return "Of course! Are you currently enrolled in any Dutch institution?"

    # Yes, I moved to the Netherlands from France to study a bachelor's degree in Den Haag Hogeschool.
    if "France" in input[0]:
        return "Great! Are you enrolled full-time?"

    # "Yes! I am"
    if "Yes! I am" in input[0]:
        return "Good luck! And do you have any job on the side?"

    # "Yes, I work at a local cafe every other Saturday"
    if "Saturday" in input[0]:
        return "Unfortunately that does not make you elegible to student finance"

    # Why?
    if "Why?" in input[0]:
        return "As a EU citizen, you need to work at least 32 hours to be elegible."

    # Ah that's great to know, thanks!
    if "to know" in input[0]:
        return "You're welcome! You can find more information for your specific case in Eligibility > Working Hours"

    return "This is a response to: " + " ".join(input)

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
    app.run(debug=True)
