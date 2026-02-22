import streamlit as st
from openai import OpenAI
import datetime

# ======================================================
# CONFIG
# ======================================================
st.set_page_config(
    page_title="CBSE Grade 10 Smart Tutor",
    page_icon="📘",
    layout="wide"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ======================================================
# SESSION STATE INIT
# ======================================================
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "xp" not in st.session_state:
    st.session_state.xp = 0

if "topic_history" not in st.session_state:
    st.session_state.topic_history = []

if "streak_date" not in st.session_state:
    st.session_state.streak_date = str(datetime.date.today())

# ======================================================
# STYLING
# ======================================================
st.markdown("""
<style>
.main { background-color: #f8fafc; }

.header {
    font-size: 34px;
    font-weight: 700;
    color: #111827;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    height: 3em;
    font-size: 15px;
    border: none;
    width: 100%;
}

.metric-box {
    background: white;
    padding: 18px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR NAVIGATION
# ======================================================
st.sidebar.title("Navigation")

if st.sidebar.button("🏠 Dashboard"):
    st.session_state.page = "Dashboard"

if st.sidebar.button("📚 Study Mode"):
    st.session_state.page = "Study"

if st.sidebar.button("📜 Exam Simulation"):
    st.session_state.page = "Papers"

if st.sidebar.button("💬 Doubt Solver"):
    st.session_state.page = "Doubt"

# ======================================================
# DATA
# ======================================================
SUBJECTS = [
    "Mathematics",
    "Science",
    "Social Science",
    "English",
    "Hindi",
    "Artificial Intelligence",
    "Information Technology"
]

YEARS = ["2024", "2023", "2022", "2021", "2020"]

# ======================================================
# DASHBOARD
# ======================================================
if st.session_state.page == "Dashboard":

    st.markdown("<div class='header'>📘 CBSE Grade 10 Smart Tutor</div>", unsafe_allow_html=True)
    st.markdown("### 90+ Academic Mode Enabled")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"<div class='metric-box'><h3>⭐ XP</h3><h2>{st.session_state.xp}</h2></div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='metric-box'><h3>📖 Topics Studied</h3><h2>{len(st.session_state.topic_history)}</h2></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## Quick Start")

    cols = st.columns(4)
    for i, subject in enumerate(SUBJECTS):
        with cols[i % 4]:
            if st.button(subject):
                st.session_state.page = "Study"

# ======================================================
# STUDY MODE (90+ ENGINE)
# ======================================================
elif st.session_state.page == "Study":

    st.markdown("## 📚 90+ Study Mode")

    subject = st.selectbox("Subject", SUBJECTS)
    chapter = st.text_input("Enter Chapter Name")

    mode = st.radio(
        "Learning Mode",
        [
            "Concept Clarity",
            "Exam-Oriented Answers",
            "Competency Case Study",
            "Practice Test (40 Marks)"
        ]
    )

    if st.button("Generate Structured Lesson"):

        if subject in ["Mathematics", "Science"]:
            temperature = 0.2
        else:
            temperature = 0.4

        prompt = f"""
You are a strict CBSE Grade 10 teacher aligned strictly to NCERT textbook.

Subject: {subject}
Chapter: {chapter}
Mode: {mode}

Follow these rules:
1. Use NCERT-based explanation only.
2. Follow CBSE blueprint.
3. Structure answer as:

### 📘 Concept Explanation
### 🧠 Key Points
### ✏ Step-by-Step Example (if numerical)
### 🎯 Exam Tip
### ❓ Practice Questions (2M, 3M, 5M)
### ✅ Answers

4. For numericals:
   - Write formula
   - Substitute values
   - Show steps clearly
   - Highlight final answer

Avoid unnecessary theory.
If unsure, mention uncertainty.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a strict NCERT-based CBSE evaluator."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )

        st.session_state.xp += 20
        st.session_state.topic_history.append((subject, chapter))

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(response.choices[0].message.content)
        st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# EXAM SIMULATION (PATTERN BASED)
# ======================================================
elif st.session_state.page == "Papers":

    st.markdown("## 📜 Exam Simulation (Blueprint Aligned)")

    subject = st.selectbox("Subject", SUBJECTS)
    year = st.selectbox("Simulate Pattern Based On Year", YEARS)

    if st.button("Generate Full Question Paper"):

        prompt = f"""
Generate a CBSE Grade 10 {subject} full-length question paper 
based on {year} pattern.

Structure:
Section A – MCQs
Section B – 2/3 mark questions
Section C – 4/5 mark long answer
Include internal choices.

Ensure realistic CBSE marking distribution.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an official CBSE paper setter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(response.choices[0].message.content)
        st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# DOUBT SOLVER
# ======================================================
elif st.session_state.page == "Doubt":

    st.markdown("## 💬 Doubt Solver")

    question = st.text_area("Ask your doubt clearly")

    if st.button("Solve Doubt") and question:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise CBSE Grade 10 teacher. Provide correct structured answers only."},
                {"role": "user", "content": question}
            ],
            temperature=0.2
        )

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(response.choices[0].message.content)
        st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# FOOTER
# ======================================================
st.markdown("""
<div style='text-align:center; padding:20px; color:#9ca3af; font-size:14px;'>
CBSE 2026 Blueprint Aligned | 90+ Strategy Mode
</div>
""", unsafe_allow_html=True)
