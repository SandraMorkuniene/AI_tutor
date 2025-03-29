import os
import openai
import streamlit as st
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize LangChain components
def initialize_langchain(language):
    # Define the prompt template based on selected language
    prompt_template = f"""
    You are a native speaker of {language}. 
    Engage in conversation with the user, correct their mistakes, and provide explanations for improvements.
    """

    # Create a memory buffer for storing the conversation history
    memory = ConversationBufferMemory(memory_key="messages", return_messages=True)

    # Initialize the OpenAI model via LangChain
    chat_model = ChatOpenAI(model="gpt-4", temperature=0.7)
    
    # Create the conversation chain with memory
    conversation_chain = ConversationChain(
        llm=chat_model,
        memory=memory,
        verbose=True
    )
    
    return conversation_chain, memory

# Function to save conversation to a text file
def save_conversation_to_text(messages):
    text_content = ""
    for message in messages:
        role = message["role"]
        content = message["content"]
        text_content += f"{role.capitalize()}: {content}\n"
    return text_content

# Function to save conversation to an Excel file
def save_conversation_to_excel(messages):
    df = pd.DataFrame(messages)
    return df

# Set up the Streamlit interface
st.title("Language Learning App: French / Italian")

# Language selection
language = st.radio("Select a language:", ("French", "Italian"))

# Initialize LangChain conversation chain
conversation_chain, memory = initialize_langchain(language)

# User input text box
user_input = st.text_area(f"Enter your message in {language}:")

# Initialize session state for storing conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Handle user input and AI response
if user_input:
    # Add user message to conversation history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Run the conversation chain with the input
    ai_response = conversation_chain.run(user_input)
    
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
