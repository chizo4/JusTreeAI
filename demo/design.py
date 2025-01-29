import streamlit as st

st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    body {
        background-image: url('background_website.png');
        background-size: cover;
        background-attachment: fixed;
    }
    .chat-container {
        position: fixed;
        right: 20px;
        bottom: 20px;
        width: 30%;
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

script = [
    {"sender": "bot", "text": "Hello! How can I help you?"},
    {"sender": "user", "text": "What is the weather like today?"},
    {"sender": "bot", "text": "It’s sunny and 25°C outside."},
    {"sender": "user", "text": "Great! Thank you."},
]

# Container to mimic a chat interface
with st.container():
    for message in script:
        if message["sender"] == "bot":
            st.markdown(f"**Bot:** {message['text']}")
        elif message["sender"] == "user":
            st.markdown(f"<div style='text-align: right;'>**You:** {message['text']}</div>", unsafe_allow_html=True)
