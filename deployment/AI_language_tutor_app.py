import streamlit as st
import openai
import pandas as pd
import io
import os
from gtts import gTTS
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# App title and language selection
st.title("🌍 AI Language Learning App")
lang = st.selectbox("Choose a language to practice:", ["French", "Italian", "Romanian"])

# Sidebar: model selection
st.sidebar.markdown("### ⚙️ Helper Model Settings")
helper_model = st.sidebar.radio("Choose model for Helper Chatbot:", ["gpt-4", "gpt-3.5-turbo", "gpt-4o"], index=1)

# Initialize session state
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "helper_conversation" not in st.session_state:
    st.session_state.helper_conversation = []

# === MAIN LANGUAGE PRACTICE === #
st.subheader(f"✍️ Practice {lang}")
user_input = st.text_area(f"Write something in {lang} (AI will correct and respond):", key="lang_input")

if st.button("Submit", key="lang_submit"):
    if user_input.strip() == "":
        st.warning("Please enter some text.")
    else:
        messages = [{"role": "system", "content": f"You are a native {lang} speaker. Help the user learn {lang} by correcting mistakes, explaining errors, and continuing the conversation."}]
        for entry in st.session_state.conversation:
            messages.append({"role": "user", "content": entry["user"]})
            messages.append({"role": "assistant", "content": entry["ai"]})
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        feedback = response.choices[0].message.content
        st.session_state.conversation.append({"user": user_input, "ai": feedback})

        st.markdown("### 🧠 AI Feedback and Response:")
        st.write(feedback)

        # TEXT-TO-SPEECH: Generate & play
        tts = gTTS(text=feedback, lang=lang[:2].lower())
        tts.save("response.mp3")
        audio_file = open("response.mp3", "rb")
        st.audio(audio_file.read(), format="audio/mp3")

# === HELPER CHATBOT IN ENGLISH === #
st.subheader("💡 Ask a question in English (Grammar, Vocabulary, etc.)")
helper_input = st.text_input("Ask something about the language you're learning:", key="helper_input")

if st.button("Ask Helper", key="helper_submit"):
    if helper_input.strip() == "":
        st.warning("Please enter a question.")
    else:
        messages = [
            {"role": "system", "content": f"You are an expert {lang} language tutor. Answer the user's questions in clear English with structured formatting (use bullet points, examples, and definitions if helpful)."},
        ]
        for entry in st.session_state.helper_conversation:
            messages.append({"role": "user", "content": entry["user"]})
            messages.append({"role": "assistant", "content": entry["ai"]})
        messages.append({"role": "user", "content": helper_input})

        response = client.chat.completions.create(
            model=helper_model,
            messages=messages
        )

        feedback = response.choices[0].message.content
        st.session_state.helper_conversation.append({"user": helper_input, "ai": feedback})

        st.markdown("### 📘 Explanation:")
        st.markdown(feedback)

# === SIDEBAR === #
st.sidebar.title("📜 Conversation History")

# Language conversation
st.sidebar.subheader(f"{lang} Conversation")
for entry in st.session_state.conversation:
    st.sidebar.markdown(f"**You:** {entry['user']}")
    st.sidebar.markdown(f"**AI:** {entry['ai']}")

# Helper Q&A
st.sidebar.subheader("English Helper Q&A")
for entry in st.session_state.helper_conversation:
    st.sidebar.markdown(f"🧑‍🏫 **Q:** {entry['user']}")
    st.sidebar.markdown(f"🤖 **A:** {entry['ai']}")

# === Downloads === #
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

# === CLEAR CONVERSATION === #
if st.sidebar.button("🧹 Clear All Conversations"):
    st.session_state.conversation = []
    st.session_state.helper_conversation = []
    st.sidebar.success("Conversations cleared. Start fresh!")
