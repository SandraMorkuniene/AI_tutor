
import os
import openai
import streamlit as st
import pandas as pd

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to handle conversation with the model
def chat_with_model(messages):
    response = openai.Completion.create(
        model="gpt-4",  # You can also use "gpt-3.5-turbo"
        prompt=generate_prompt(messages),
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Function to generate the prompt
def generate_prompt(messages):
    prompt = ""
    for message in messages:
        role = message["role"]
        content = message["content"]
        prompt += f"{role.capitalize()}: {content}\n"
    prompt += "Assistant: "
    return prompt

# Function to save conversation history as a text file
def save_conversation_to_text(messages):
    text_content = ""
    for message in messages:
        role = message["role"]
        content = message["content"]
        text_content += f"{role.capitalize()}: {content}\n"
    return text_content

# Function to save conversation history as an Excel file
def save_conversation_to_excel(messages):
    df = pd.DataFrame(messages)
    return df

# Set up the Streamlit interface
st.title("Language Learning App: French / Italian")

# Language selection
language = st.radio("Select a language:", ("French", "Italian"))

# User input text box
user_input = st.text_area(f"Enter your message in {language}:")

# Initialize session state for storing conversation history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"You are a native speaker of {language}."}
    ]

# Handle user input and AI response
if user_input:
    # Add user message to conversation history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate response from the model
    ai_response = chat_with_model(st.session_state.messages)

    # Add AI response to conversation history
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    # Display the conversation history
    st.write("### Conversation History:")
    for message in st.session_state.messages:
        st.write(f"{message['role'].capitalize()}: {message['content']}")

# Provide an option to download the conversation
st.sidebar.header("Download Conversation")
if st.session_state.messages:
    # Provide download as text
    text_content = save_conversation_to_text(st.session_state.messages)
    st.sidebar.download_button("Download as Text File", text_content, file_name="conversation.txt")

    # Provide download as Excel
    excel_content = save_conversation_to_excel(st.session_state.messages)
    st.sidebar.download_button("Download as Excel File", excel_content.to_csv(index=False), file_name="conversation.csv")
