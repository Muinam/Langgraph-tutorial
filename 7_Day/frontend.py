import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage

st.set_page_config(page_title="AI Chatbot", page_icon="💬", layout="centered")

st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1e1e2f 0%, #11111d 100%);
        color: #ffffff;
    }
    .stTextInput>div>div>input {
        background-color: #252538;
        color: white;
        border: 1px solid #4f4f7a;
    }
    .user-box {
        background-color: #2e2e4a;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #6c5ce7;
    }
    .ai-box {
        background-color: #1e1e2f;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #00cec9;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💬 LangGraph AI Chatbot")

# Initialize session state for displaying user input and AI message
if 'user_message' not in st.session_state:
    st.session_state['user_message'] = ""
if 'ai_response' not in st.session_state:
    st.session_state['ai_response'] = ""

user_input = st.text_input("Type your message here:", key="user_input_box")

if st.button("Send", use_container_width=True) and user_input:
    # Save the user input
    st.session_state['user_message'] = user_input
    
    # Get the AI response
    config = {'configurable': {'thread_id': 'thread-1'}}
    try:
        response = chatbot.invoke(
            {'messages': [HumanMessage(content=user_input)]},
            config=config
        )
        st.session_state['ai_response'] = response['messages'][-1].content
    except Exception as e:
        st.session_state['ai_response'] = f"Error: {str(e)}"

# Display boxes
if st.session_state['user_message']:
    st.markdown("### 👤 User Message")
    st.markdown(f"<div class='user-box'>{st.session_state['user_message']}</div>", unsafe_allow_html=True)

if st.session_state['ai_response']:
    st.markdown("### 🤖 AI Message")
    st.markdown(f"<div class='ai-box'>{st.session_state['ai_response']}</div>", unsafe_allow_html=True)
