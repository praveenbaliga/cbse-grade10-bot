import streamlit as st
from openai import OpenAI

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="CBSE Grade 10 AI Tutor",
    page_icon="📚",
    layout="wide"
)

# =============================
# OPENAI CLIENT
# =============================
if "OPENAI_API_KEY" not in st.secrets:
    st.error("OpenAI API Key not found. Please add OPENAI_API_KEY in HuggingFace Secrets.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# =============================
# PROMPT BUILDER
# =============================
def build_prompt(subject, chapter, mode):

    system_prompt = """
You are a strict CBSE Grade 10 academic expert aligned with NCERT syllabus.
Follow CBSE 2026 pattern.
Ensure minimum 40% competency-based questions.
Use clear headings.
Give accurate answers only.
Avoid unnecessary explanations.
"""

    user_prompt = f"""
Subject: {subject}
Chapter: {chapter}
Mode: {mode}

Generate structured academic content accordingly.
"""

    return system_prompt, user_prompt


# =============================
# GENERATE CONTENT
# =============================
def generate_content(subject, chapter, mode):

    system_prompt, user_prompt = build_prompt(subject, chapter, mode)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5,
        max_tokens=1000
    )

    return response.choices[0].message.content


# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.title("🎯 Select Options")

    subject = st.selectbox("Subject", [
        "Mathematics",
        "Science",
        "Social Science",
        "English",
        "Hindi",
        "AI",
        "IT"
    ])

    chapter = st.selectbox("Chapter", [
        "Chapter 1",
        "Chapter 2",
        "Chapter 3"
    ])

    mode = st.selectbox("Mode", [
        "Chapter Summary",
        "Mock Test 40 Marks",
        "Important Board Questions",
        "MCQs with Answers",
        "Case Study Questions"
    ])

    generate_btn = st.button("🚀 Generate Content", use_container_width=True)


# =============================
# MAIN UI
# =============================
st.title("🧑‍🏫 CBSE Grade 10 Personal AI Tutor")

if generate_btn:
    with st.spinner("Generating CBSE-aligned content..."):
        try:
            result = generate_content(subject, chapter, mode)
            st.markdown(result)
        except Exception as e:
            st.error(f"Error: {e}")


# =============================
# DOUBT CHAT SECTION
# =============================
st.markdown("---")
st.subheader("💬 Ask Doubts")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask any doubt..."):
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                temperature=0.5,
                max_tokens=800
            )

            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"Error: {e}")
