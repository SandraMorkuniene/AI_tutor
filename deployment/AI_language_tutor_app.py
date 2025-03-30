import streamlit as st
import openai
import pandas as pd
import io
import os

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Title and language selection
st.title("🌍 AI Language Learning App")
lang = st.selectbox("Choose a language to practice:", ["French", "Italian", "Romanian"])

# Initialize session state for conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# User input
user_input = st.text_area("Write something in " + lang + " (AI will correct and respond)")

if st.button("Submit"):
    if user_input.strip() == "":
        st.warning("Please enter some text.")
    else:
        # Construct conversation history for context
        messages = [{"role": "system", "content": f"You are a native {lang} speaker. Help the user learn {lang} by correcting mistakes, explaining errors, and continuing the conversation."}]
        for entry in st.session_state.conversation:
            messages.append({"role": "user", "content": entry["user"]})
            messages.append({"role": "assistant", "content": entry["ai"]})
        
        messages.append({"role": "user", "content": user_input})
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        
        feedback = response["choices"][0]["message"]["content"]
        
        # Save conversation history
        st.session_state.conversation.append({"user": user_input, "ai": feedback})
        
        st.markdown("### AI Feedback and Response:")
        st.write(feedback)

# Display conversation history
st.sidebar.title("📜 Conversation History")
for entry in st.session_state.conversation:
    st.sidebar.markdown(f"**You:** {entry['user']}")
    st.sidebar.markdown(f"**AI:** {entry['ai']}")

# Download conversation history
if st.sidebar.button("Download Conversation (Excel)"):
    df = pd.DataFrame(st.session_state.conversation)
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, sheet_name="Conversation")
    towrite.seek(0)
    st.sidebar.download_button(
        label="📥 Download Excel File",
        data=towrite,
        file_name="conversation_history.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if st.sidebar.button("Download Conversation (Text)"):
    text_history = "\n".join([f"You: {entry['user']}\nAI: {entry['ai']}" for entry in st.session_state.conversation])
    st.sidebar.download_button(
        label="📥 Download Text File",
        data=text_history,
        file_name="conversation_history.txt",
        mime="text/plain"
    )
