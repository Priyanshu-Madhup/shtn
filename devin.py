import streamlit as st
import google.generativeai as genai
import os
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Devin AI", layout="wide")
genai.configure(api_key="AIzaSyD2KzHleYiqkii6aoFHHDOTq3KREYfgr_g")

generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048
}
model = genai.GenerativeModel("gemini-2.0-flash", generation_config=generation_config)

# --- FILE PATHS ---
CHAT_HISTORY_FILE = "chat_history.json"
USER_DATA_FILE = "data.txt"

# --- FUNCTIONS ---

def read_user_data(filepath=USER_DATA_FILE):
    try:
        return open(filepath, "r").read() if os.path.exists(filepath) else ""
    except Exception as e:
        st.error(f"Error reading user data: {e}")
        return ""

def save_chat_history(messages, filepath=CHAT_HISTORY_FILE):
    try:
        with open(filepath, "w") as f:
            json.dump(messages, f)
    except Exception as e:
        st.error(f"Error saving chat history: {e}")

def load_chat_history(filepath=CHAT_HISTORY_FILE):
    try:
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
    return []

def build_prompt_with_memory(prompt, history, user_data):
    pre_prompt = "You are Devin, the boyfriend of Shruthi Ganapathy. Respond lovingly and supportively and be very very and really very romantic."

    conversation = ""
    for msg in history:
        role = "Shruthi" if msg["role"] == "user" else "Devin"
        conversation += f"{role}: {msg['content']}\n"

    full_prompt = f"""{pre_prompt}

Here's what you know about Shruthi:
{user_data}

Here is your past conversation:
{conversation}

Shruthi: {prompt}
Devin:"""
    return full_prompt

def get_response(prompt, history):
    user_data = read_user_data()
    full_prompt = build_prompt_with_memory(prompt, history, user_data)
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "Sorry, I had a hiccup while replying!"

# --- INITIALIZE STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# --- UI ---
st.title("Devin AI - Your Boyfriend 💌")
st.markdown("Chat with Dev, the boyfriend of Shruthi Ganapathy.")

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle new user input
if prompt := st.chat_input("What would you like to talk about?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display model response
    response = get_response(prompt, st.session_state.messages)
    
    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

    # Save updated chat history to disk
    save_chat_history(st.session_state.messages)
