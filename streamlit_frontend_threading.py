import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# ============================== PAGE CONFIG ====================================

st.set_page_config(
    page_title="LangGraph Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ============================== CUSTOM CSS =====================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

[data-testid="stSidebar"] {
    background-color: #161A23;
}

.chat-title {
    font-size: 38px;
    font-weight: bold;
    color: white;
    margin-bottom: 5px;
}

.chat-subtitle {
    color: #9CA3AF;
    margin-bottom: 25px;
}

.user-msg {
    background-color: #2563EB;
    padding: 12px 16px;
    border-radius: 14px;
    color: white;
    margin-bottom: 10px;
    width: fit-content;
    max-width: 80%;
    margin-left: auto;
}

.ai-msg {
    background-color: #1F2937;
    padding: 12px 16px;
    border-radius: 14px;
    color: white;
    margin-bottom: 10px;
    width: fit-content;
    max-width: 80%;
}

.stButton>button {
    border-radius: 10px;
    border: none;
    padding: 0.5rem 1rem;
    font-weight: 600;
}

.sidebar-chat button {
    text-align: left;
    width: 100%;
}

</style>
""", unsafe_allow_html=True)

# ============================== UTILITY FUNCTIONS ==============================

def generate_thread_id():
    return str(uuid.uuid4())[:8]


def generate_chat_title(message):

    words = message.strip().split()

    title = " ".join(words[:5])

    if len(words) > 5:
        title += "..."

    return title


def add_thread(thread_id, title="New Chat"):

    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'][thread_id] = title


def reset_chat():

    new_thread = generate_thread_id()

    st.session_state['thread_id'] = new_thread
    st.session_state['message_history'] = []

    add_thread(new_thread)


def load_conversation(thread_id):

    state = chatbot.get_state(
        config={'configurable': {'thread_id': thread_id}}
    )

    return state.values.get('messages', [])


# ============================== SESSION SETUP ==================================

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = {}

add_thread(st.session_state['thread_id'])

# ============================== SIDEBAR ========================================

with st.sidebar:

    st.title("🤖 LangGraph")

    st.markdown("---")

    if st.button("➕ New Chat", use_container_width=True):
        reset_chat()

    st.markdown("### 💬 Conversations")

    for thread_id, title in reversed(
        list(st.session_state['chat_threads'].items())
    ):

        if st.button(
            f"💬 {title}",
            key=thread_id,
            use_container_width=True
        ):

            st.session_state['thread_id'] = thread_id

            messages = load_conversation(thread_id)

            temp_messages = []

            for msg in messages:

                role = (
                    "user"
                    if isinstance(msg, HumanMessage)
                    else "assistant"
                )

                temp_messages.append({
                    "role": role,
                    "content": msg.content
                })

            st.session_state['message_history'] = temp_messages

# ============================== HEADER =========================================

st.markdown(
    '<div class="chat-title">🤖 AI Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="chat-subtitle">Powered by LangGraph + Streamlit</div>',
    unsafe_allow_html=True
)

# ============================== DISPLAY MESSAGES ===============================

for message in st.session_state['message_history']:

    with st.chat_message(message['role']):

        if message['role'] == 'user':

            st.markdown(
                f'<div class="user-msg">{message["content"]}</div>',
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f'<div class="ai-msg">{message["content"]}</div>',
                unsafe_allow_html=True
            )

# ============================== CHAT INPUT =====================================

user_input = st.chat_input("Type your message...")

if user_input:

    # Generate title from first message
    thread_id = st.session_state['thread_id']

    if st.session_state['chat_threads'][thread_id] == "New Chat":

        st.session_state['chat_threads'][thread_id] = (
            generate_chat_title(user_input)
        )

    # Store user message
    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })

    # Display user message
    with st.chat_message('user'):

        st.markdown(
            f'<div class="user-msg">{user_input}</div>',
            unsafe_allow_html=True
        )

    CONFIG = {
        'configurable': {
            'thread_id': st.session_state['thread_id']
        }
    }

    # ============================== AI RESPONSE ==============================

    with st.chat_message("assistant"):

        def ai_only_stream():

            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):

                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    # Store AI message
    st.session_state['message_history'].append({
        'role': 'assistant',
        'content': ai_message
    })