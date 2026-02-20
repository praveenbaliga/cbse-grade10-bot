import streamlit as st
import requests
import json

# Hugging Face API setup (free tier)
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
HF_TOKEN = st.secrets.get("HF_TOKEN", "")  # Add your token in Spaces secrets

def query_llm(prompt):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": f"CBSE Grade 10 NCERT expert: {prompt}",
        "parameters": {"max_new_tokens": 500, "temperature": 0.7}
    }
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    return response.json()[0]["generated_text"] if response.ok else "API busy, try again."

st.set_page_config(page_title="CBSE Grade 10 Bot", layout="wide")
st.title("🧑‍🏫 CBSE Grade 10 NCERT Study Helper")
st.markdown("Ask for mock papers, chapter summaries, evaluations per NCERT syllabus (Maths, Science, etc.). Strictly CBSE-aligned.[web:21][web:24]")

# Sidebar for subject/chapter selection
with st.sidebar:
    st.header("Select Mode")
    mode = st.selectbox("Choose:", ["Mock Exam", "Chapter Summary", "Evaluate Answer", "Sample Questions"])
    subject = st.selectbox("Subject:", ["Mathematics", "Science", "Social Science", "English", "Hindi", "AI", "IT"])
    chapters = st.text_input("Chapters (e.g., 'Ch1-3')") if mode != "Evaluate Answer" else ""
    marks = st.slider("Marks:", 40, 100, 80) if "Mock" in mode else ""

# Main chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about CBSE Grade 10 (e.g., 'Create Maths mock paper 80 marks')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if mode == "Mock Exam":
            llm_prompt = f"Generate CBSE Grade 10 {subject} mock paper {marks} marks on {chapters}, NCERT syllabus. Follow pattern: MCQs(20%), 2/3/4m, case-study(10%), choices. Time: 3hrs.[web:22][web:25]"
        elif mode == "Chapter Summary":
            llm_prompt = f"Summarise NCERT Class 10 {subject} {chapters}: Background, Key Concepts, Definitions, 5 board Qs, 5 MCQs, 3 A/R.[web:21]"
        elif mode == "Evaluate Answer":
            llm_prompt = f"Evaluate this answer for CBSE Grade 10 {subject}: {prompt}. Step marks, mistake type (concept/calc), 5 practice Qs."
        else:
            llm_prompt = f"CBSE Grade 10 {subject} {mode} for {chapters}: NCERT strict."
        
        with st.spinner("Generating..."):
            response = query_llm(llm_prompt)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
