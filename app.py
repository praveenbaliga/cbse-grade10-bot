import streamlit as st
import requests
import time
import os

# Page config
st.set_page_config(
    page_title="CBSE Grade 10 AI Tutor", 
    page_icon="📚",
    layout="wide"
)

# HF API setup - FASTER MODEL + RETRY LOGIC
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

def query_llm(prompt, max_retries=5):
    """Robust LLM query with retries and fallbacks"""
    if not HF_TOKEN.startswith("hf_"):
        return "⚠️ Please add HF_TOKEN in Settings → Secrets for full AI responses"
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    for attempt in range(max_retries):
        try:
            payload = {
                "inputs": f"CBSE Class 10 NCERT Expert. Strictly NCERT syllabus. Follow CBSE paper pattern. User: {prompt}",
                "parameters": {
                    "max_new_tokens": 600,
                    "temperature": 0.1,
                    "do_sample": False,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                HF_API_URL, 
                headers=headers, 
                json=payload, 
                timeout=45
            )
            
            if response.ok and response.json():
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get("generated_text", "")
                    return text.strip()
            
            # Model loading, wait longer
            if "model is currently loading" in response.text.lower():
                wait_time = 2 ** attempt
                st.info(f"🤖 Model warming up... waiting {wait_time}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
                continue
                
        except Exception as e:
            time.sleep(2 ** attempt)
    
    # Graceful fallback
    return f"""
📚 **CBSE Grade 10 Demo Mode Active**
Model temporarily busy (peak hours). 

**Quick Actions Available:**
- Select **Mock Exam** → 80 marks paper
- Choose **Chapter Summary** → Key concepts + 5 board Qs  
- Pick **Subject** from sidebar

**Full LLM responses will work shortly!**
Try again or select different mode.
    """

# Header
st.title("🧑‍🏫 CBSE Grade 10 NCERT AI Tutor")
st.markdown("**Strictly NCERT syllabus • CBSE 2026 paper pattern • Competency-based questions**")

# Sidebar controls
st.sidebar.header("📋 Select Study Mode")
mode = st.sidebar.selectbox("Choose Mode:", [
    "Mock Exam", "Chapter Summary", "Evaluate Answer", 
    "Sample Questions", "Rapid Revision"
])

subject = st.sidebar.selectbox("Subject:", [
    "Mathematics", "Science", "Social Science", 
    "English", "Hindi A", "Hindi B", "Artificial Intelligence", "Information Technology"
])

if mode != "Evaluate Answer":
    chapters = st.sidebar.text_input("Chapters:", placeholder="Ch1-3 or Full syllabus")
    marks = st.sidebar.slider("Marks:", 40, 100, 80) if "Mock" in mode else 0

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask anything about CBSE Grade 10 (e.g., 'Maths Ch1 summary', 'Science 80 marks paper')"):
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response based on mode
    with st.chat_message("assistant"):
        with st.spinner("Generating CBSE content..."):
            
            if mode == "Mock Exam":
                llm_prompt = f"""
CBSE Class 10 {subject} MOCK PAPER ({marks} marks, 3 hours)
📋 Strictly NCERT syllabus {chapters}
✅ 20% MCQs, 20% VSA (2m), 20% SA (3m), 27% LA (4m), 13% Case Study
✅ Internal choices in Q27-34
✅ Competency-based questions (minimum 40%)
Generate COMPLETE question paper with instructions.
                """
                
            elif mode == "Chapter Summary":
                llm_prompt = f"""
NCERT Class 10 {subject} Chapter {chapters} SUMMARY
📖 Background + Key Concepts + Definitions
📚 Important dates/people/places (if History/Geography)
✅ 5 Likely Board Questions (2m,3m,4m,5m marks)
✅ 5 MCQs with 4 options
✅ 3 Assertion-Reason questions
Strictly NCERT textbook content only.
                """
                
            elif mode == "Evaluate Answer":
                llm_prompt = f"""
EVALUATE student answer for CBSE Class 10 {subject}:
Student answer: {prompt}

CBSE MARKING:
✅ Step-wise marks allocation
✅ Identify mistake type: Concept/Formula/Calculation/Presentation
✅ Award marks out of total
✅ Suggest 5 targeted practice questions
                """
                
            else:  # Sample Questions, Revision
                llm_prompt = f"""
CBSE Class 10 {subject} {mode} ({chapters})
Generate 10 high-weightage questions per NCERT syllabus.
Follow latest CBSE blueprint and paper pattern.
                """

            response = query_llm(llm_prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown("*Strictly aligned with NCERT textbooks • CBSE 2025-26 pattern • Powered by Hugging Face AI*")
