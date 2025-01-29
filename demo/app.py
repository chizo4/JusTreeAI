from flask import Flask, render_template, request, jsonify
from typing import List

app = Flask(__name__)

# Your chatbot function
def get_response_from_bot(input: List[str]) -> str:

    if input[0] == "Hello":
        return "Hi! How can I help you?"

    if input[0] == "My name is Lydia, I just moved to the Netherlands from France to study a bachelor degree in the Den Haag Hogeschool. I am currently enrolled full-time.":
        return "Great Lydia, could I ask whether you currently work alongside your studies?"
    
    if input[0] == "I am! Currently I am working every second Saturday in a local cafe.":
        return "Unfortunately Lydia, you are not yet eligible for the student finance. However, you would be eligible if you increase your current working hours to 32 hours a month."

    if input[0] == "Oh perfect! I will ask my employer to work every Saturday in that case, that should make me eligible and help with my studies. Thank you!":
        return "You can find more information in Eligibility > Working Hours"

    return "This is a response to: " + " ".join(input)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    bot_response = get_response_from_bot([user_message])
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
