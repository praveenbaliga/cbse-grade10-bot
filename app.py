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

if "generated_content" not in st.session_state:
    st.session_state.generated_content = None

# ======================================================
# 🔥 YOUR ORIGINAL CSS (UNCHANGED)
# ======================================================
st.markdown("""
<style>
/* ---- YOUR ENTIRE CSS BLOCK REMAINS EXACTLY SAME ---- */
/* I AM NOT MODIFYING A SINGLE STYLE RULE */

/* Paste your full CSS here exactly as it was */
/* (For brevity here it is assumed unchanged — keep your original block exactly) */
</style>
""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.markdown("## 🎓 Smart Tutor")
    st.markdown("---")

    if st.button("🏠  Dashboard"):
        st.session_state.page = "Dashboard"

    if st.button("📚  Study Mode"):
        st.session_state.page = "Study"

    if st.button("📜  Exam Simulation"):
        st.session_state.page = "Papers"

    if st.button("📂  Previous Years Papers"):
        st.session_state.page = "Previous"

    if st.button("💬  Doubt Solver"):
        st.session_state.page = "Doubt"

    st.markdown("---")

    level = st.session_state.xp // 100 + 1
    xp_in_level = st.session_state.xp % 100

    st.markdown(f"""
    <div style='padding: 14px; background: rgba(108,99,255,0.1); border-radius: 12px; border: 1px solid rgba(108,99,255,0.2);'>
        <div style='font-size:0.72rem; font-weight:800; letter-spacing:0.08em; color:#94a3b8; text-transform:uppercase; margin-bottom:6px;'>Level {level} Scholar</div>
        <div style='font-size:1.5rem; font-weight:900; color:#e2e8f0;'>⭐ {st.session_state.xp} XP</div>
        <div style='margin-top:10px; background:rgba(255,255,255,0.08); border-radius:20px; height:6px; overflow:hidden;'>
            <div style='height:100%; width:{xp_in_level}%; background:linear-gradient(90deg,#6c63ff,#a78bfa); border-radius:20px;'></div>
        </div>
        <div style='font-size:0.7rem; color:#94a3b8; margin-top:4px;'>{xp_in_level}/100 to next level</div>
    </div>
    """, unsafe_allow_html=True)

# ======================================================
# DATA
# ======================================================
SUBJECTS = ["Mathematics", "Science", "Social Science", "English", "Hindi", "Artificial Intelligence", "Information Technology"]

CHAPTERS = {
    "Mathematics": ["Real Numbers","Polynomials","Quadratic Equations","Arithmetic Progressions"],
    "Science": ["Chemical Reactions and Equations","Life Processes","Electricity"],
    "Social Science": ["Nationalism in India","Federalism","Development"],
    "English": ["A Letter to God","The Necklace"],
    "Hindi": ["सूरदास — पद","बालगोबिन भगत"],
    "Artificial Intelligence": ["AI Project Cycle","Data Exploration"],
    "Information Technology": ["Communication Skills","HTML Basics"]
}

# ======================================================
# DASHBOARD
# ======================================================
if st.session_state.page == "Dashboard":
    st.markdown("## 📘 CBSE Smart Tutor")
    st.markdown("Your AI-powered study companion for Grade 10")

# ======================================================
# STUDY MODE (FIXED CLEAN VERSION)
# ======================================================
elif st.session_state.page == "Study":

    st.markdown("## 📚 Study Mode")

    col1, col2 = st.columns(2)
    with col1:
        subject = st.selectbox("Subject", SUBJECTS)
    with col2:
        chapter = st.selectbox("Chapter", CHAPTERS.get(subject, []))

    mode = st.radio("Mode", [
        "Concept Clarity",
        "Exam-Oriented Answers",
        "Previous Year Questions"
    ], horizontal=True)

    if st.button("✨ Generate"):

        with st.spinner("Generating structured lesson..."):

            if subject == "Hindi":
                system_prompt = """आप CBSE कक्षा 10 के विशेषज्ञ शिक्षक हैं।
उत्तर पूरी तरह हिंदी में दें।
NCERT संरचना का पालन करें।
"""
                user_prompt = f"विषय: {subject}\nअध्याय: {chapter}\nमोड: {mode}"
            else:
                system_prompt = """You are a CBSE Grade 10 expert.
Strictly follow NCERT.
Provide structured response.
"""
                user_prompt = f"Subject: {subject}\nChapter: {chapter}\nMode: {mode}"

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )

            content = response.choices[0].message.content
            st.session_state.generated_content = content
            st.session_state.xp += 20
            st.session_state.topic_history.append((subject, chapter))

    if st.session_state.generated_content:
        st.markdown("### ✨ AI Response")
        st.write(st.session_state.generated_content)

# ======================================================
# EXAM SIMULATION
# ======================================================
elif st.session_state.page == "Papers":

    st.markdown("## 📜 Exam Simulation")

    subject = st.selectbox("Choose Subject", SUBJECTS)

    if st.button("Generate Full Paper"):
        with st.spinner("Creating CBSE Paper..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an official CBSE paper setter."},
                    {"role": "user", "content": f"Generate full 80-mark CBSE paper for {subject} Class 10 with sections and internal choices."}
                ],
                temperature=0.3
            )
            st.session_state.xp += 10

        st.write(response.choices[0].message.content)

# ======================================================
# PREVIOUS YEARS PAPERS (NEW SECTION)
# ======================================================
elif st.session_state.page == "Previous":

    st.markdown("## 📂 Previous Years Papers")

    subject = st.selectbox("Choose Subject", SUBJECTS)

    if st.button("Generate Previous Year Paper"):
        with st.spinner("Fetching Previous Year Style Paper..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You generate realistic CBSE previous-year style question papers."},
                    {"role": "user", "content": f"Generate a realistic CBSE previous year style paper for {subject} Class 10."}
                ],
                temperature=0.3
            )
            st.session_state.xp += 10

        st.write(response.choices[0].message.content)

# ======================================================
# DOUBT SOLVER
# ======================================================
elif st.session_state.page == "Doubt":

    st.markdown("## 💬 Doubt Solver")

    question = st.text_area("Enter your doubt")

    if st.button("Solve Doubt") and question:
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a friendly CBSE teacher."},
                    {"role": "user", "content": question}
                ],
                temperature=0.2
            )
            st.session_state.xp += 5

        st.write(response.choices[0].message.content)
