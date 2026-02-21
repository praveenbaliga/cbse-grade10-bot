import streamlit as st
from openai import OpenAI
import random

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Super Study Quest",
    page_icon="🚀",
    layout="centered"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==============================
# SESSION STATE INIT
# ==============================
if "xp" not in st.session_state:
    st.session_state.xp = 0

if "streak" not in st.session_state:
    st.session_state.streak = 1

if "subject" not in st.session_state:
    st.session_state.subject = None

# ==============================
# BRIGHT GAMIFIED UI
# ==============================
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.title {
    text-align:center;
    font-size:34px;
    font-weight:800;
    color:#1e3a8a;
}

.subtitle {
    text-align:center;
    font-size:18px;
    color:#374151;
    margin-bottom:20px;
}

.card {
    background-color:white;
    padding:20px;
    border-radius:20px;
    box-shadow:0px 8px 18px rgba(0,0,0,0.1);
    margin-bottom:20px;
}

.stButton>button {
    background: linear-gradient(45deg, #ff6a00, #ee0979);
    color: white;
    border-radius: 14px;
    height: 3.2em;
    font-size: 18px;
    border: none;
    width: 100%;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
student_name = "Champion"  # change to her name

st.markdown(f"<div class='title'>🚀 Hi {student_name}!</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Ready to level up your brain today? 🎯</div>", unsafe_allow_html=True)

# ==============================
# XP + STREAK DISPLAY
# ==============================
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### ⭐ XP: {st.session_state.xp}")

with col2:
    st.markdown(f"### 🔥 Streak: {st.session_state.streak} days")

st.markdown("---")

# ==============================
# DAILY CHALLENGE
# ==============================
st.markdown("## 🎯 Daily Challenge")

if st.button("Start Today’s Challenge"):

    st.session_state.xp += 10
    st.session_state.streak += 1

    st.success("🎉 +10 XP Earned!")
    st.balloons()

# ==============================
# SUBJECT SELECTION
# ==============================
st.markdown("## 📚 Choose Your Mission")

if st.button("📐 Mathematics"):
    st.session_state.subject = "Mathematics"

if st.button("🧪 Science"):
    st.session_state.subject = "Science"

if st.button("🌍 Social Science"):
    st.session_state.subject = "Social Science"

# ==============================
# SYLLABUS
# ==============================
CBSE_SYLLABUS = {
    "Mathematics": [
        "Real Numbers",
        "Quadratic Equations",
        "Trigonometry",
        "Statistics",
        "Probability"
    ],
    "Science": [
        "Chemical Reactions",
        "Life Processes",
        "Electricity",
        "Light"
    ],
    "Social Science": [
        "Nationalism in India",
        "Federalism",
        "Democracy"
    ]
}

# ==============================
# LESSON GENERATION
# ==============================
if st.session_state.subject:

    st.markdown(f"## 📖 {st.session_state.subject}")

    chapter = st.selectbox(
        "Choose Chapter",
        CBSE_SYLLABUS[st.session_state.subject]
    )

    mode = st.radio(
        "Choose Mode",
        ["Quick Summary", "Important Questions", "Practice Challenge"]
    )

    if st.button("🚀 Start Mission"):

        with st.spinner("Powering up your lesson... ⚡"):

            prompt = f"""
            You are an energetic CBSE Grade 10 teacher.
            Subject: {st.session_state.subject}
            Chapter: {chapter}
            Mode: {mode}

            Make it bright, engaging, simple and structured.
            Add examples and small quiz questions.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a fun and energetic CBSE teacher."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            output = response.choices[0].message.content

        st.session_state.xp += 20

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🧠 Mission Briefing")
        st.write(output)
        st.markdown("</div>", unsafe_allow_html=True)

        st.success("🏆 +20 XP Earned!")
        st.balloons()

# ==============================
# BADGE SYSTEM
# ==============================
st.markdown("---")
st.markdown("## 🏅 Achievements")

if st.session_state.xp >= 50:
    st.success("🌟 Brain Booster Badge Unlocked!")

if st.session_state.xp >= 100:
    st.success("🚀 Study Star Badge Unlocked!")

# ==============================
# DOUBT SOLVER
# ==============================
st.markdown("---")
st.markdown("## 💬 Ask AI Coach")

question = st.text_input("Ask anything you don’t understand")

if st.button("Get Help") and question:

    with st.spinner("Thinking hard... 🤔"):

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly CBSE Grade 10 tutor."},
                {"role": "user", "content": question}
            ]
        )

        answer = response.choices[0].message.content

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write(answer)
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# FOOTER
# ==============================
st.markdown("""
<div style='text-align:center; padding:20px; font-size:14px;'>
Level up daily. Small steps. Big success. 🚀
</div>
""", unsafe_allow_html=True)
