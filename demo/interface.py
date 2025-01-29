import streamlit as st
from streamlit_chat import message
import time
from PIL import Image
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    try:
        bin_str = get_base64_of_bin_file(png_file)
        page_bg_img = '''
        <style>
        .stApp {
            background-image: url("data:image/png;base64,%s");
            background-size: cover;
            transition: background-image 0.5s ease-in-out;
        }
        </style>
        ''' % bin_str
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except:
        st.write("Background image not found")

def simulate_typing(text, input_placeholder):
    displayed_message = ""
    for char in text:
        displayed_message += char
        input_placeholder.text_input("Type a message...", value=displayed_message, key=f"input_{len(displayed_message)}")
        time.sleep(0.03)
        st.experimental_rerun()
    return displayed_message

def toggle_chat():

    set_background("background_website.png")
    st.session_state.chat_visible = not st.session_state.chat_visible
    st.session_state.current_input = ""

def handle_chat_input():
    if not st.session_state.typing:
        st.session_state.typing = True
        st.session_state.needs_rerun = True

def main():
    # Set page config
    st.set_page_config(
        page_title="Student Finance Chatbot",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state variables
    if 'chat_visible' not in st.session_state:
        st.session_state.chat_visible = False
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_step' not in st.session_state:
        st.session_state.conversation_step = 0
    if 'typing' not in st.session_state:
        st.session_state.typing = False
    if 'needs_rerun' not in st.session_state:
        st.session_state.needs_rerun = False
    if 'current_input' not in st.session_state:
        st.session_state.current_input = ""

    # Set initial background
    if not st.session_state.chat_visible:
        set_background("background_website.png")

    # CSS styles
    st.markdown("""
    <style>
        .chat-container {
            position: fixed;
            bottom: 105px;
            right: 80px;
            width: 400px;
            height: 600px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            z-index: 99;
        }
        
        .chat-header {
            padding: 15px;
            background: #075E54;
            color: white;
            font-weight: bold;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }
        
        .chat-messages {
            flex-grow: 1;
            overflow-y: auto;
            padding: 15px;
            background: #ECE5DD;
        }
        
        .chat-input {
            padding: 15px;
            background: white;
            border-top: 1px solid #ddd;
        }
        
        .typing-indicator {
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
            margin-bottom: 10px;
        }

        /* Message styling */
        .message-user {
            background: #DCF8C6;
            padding: 10px;
            border-radius: 10px;
            margin: 5px;
            max-width: 80%;
            align-self: flex-end;
        }
        
        .message-bot {
            background: white;
            padding: 10px;
            border-radius: 10px;
            margin: 5px;
            max-width: 80%;
            align-self: flex-start;
        }
    </style>
    """, unsafe_allow_html=True)

    # Chat toggle button
    col1, col2, col3 = st.columns([6, 6, 1])
    with col3:
        st.button("💬", key="main_toggle", on_click=toggle_chat)

    # Chat interface
    if st.session_state.chat_visible:
        chat_container = st.container()
        
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            st.markdown('<div class="chat-header">Student Finance Chat</div>', unsafe_allow_html=True)
            st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
            
            # Display messages
            messages_container = st.container()
            with messages_container:
                for i, (sender, msg) in enumerate(st.session_state.messages):
                    message(msg, is_user=(sender == "user"), key=f"msg_{i}")
            
            # Typing indicator
            if st.session_state.typing:
                st.markdown('<div class="typing-indicator">Typing...</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Input area
            st.markdown('<div class="chat-input">', unsafe_allow_html=True)
            input_placeholder = st.empty()
            input_placeholder.text_input("Type a message...", 
                                      value=st.session_state.current_input,
                                      key="chat_input",
                                      on_change=handle_chat_input)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Handle conversation flow
    conversation_flow = [
        ("user", "My name is Lydia, I just moved to the Netherlands from France to study a bachelor degree in the Den Haag Hogeschool. I am currently enrolled full-time."),
        ("bot", "Great Lydia, could I ask whether you currently work alongside your studies?"),
        ("user", "I am! Currently I am working every second Saturday in a local cafe."),
        ("bot", "Unfortunately Lydia, you are not yet eligible for the student finance. However, you would be eligible if you increase your current working hours to 32 hours a month."),
        ("user", "Oh perfect! I will ask my employer to work every Saturday in that case, that should make me eligible and help with my studies. Thank you!")
    ]

    if st.session_state.typing and st.session_state.conversation_step < len(conversation_flow):
        sender, text = conversation_flow[st.session_state.conversation_step]
        
        if sender == "user":
            # Simulate typing in the input field
            st.session_state.current_input = simulate_typing(text, input_placeholder)
            time.sleep(0.5)
            
            # Add message to chat
            st.session_state.messages.append((sender, st.session_state.current_input))
            st.session_state.current_input = ""
            
            # Add bot response after delay
            if st.session_state.conversation_step + 1 < len(conversation_flow):
                time.sleep(1)
                next_sender, next_text = conversation_flow[st.session_state.conversation_step + 1]
                st.session_state.messages.append((next_sender, next_text))
                st.session_state.conversation_step += 2
        
        st.session_state.typing = False
        st.experimental_rerun()

if __name__ == "__main__":
    main()