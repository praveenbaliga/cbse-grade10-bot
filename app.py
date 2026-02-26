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

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

if "generated_content" not in st.session_state:
    st.session_state.generated_content = None

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

.stButton>button:disabled {
    background-color: #9ca3af;
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
# SIDEBAR NAVIGATION (RESTORED)
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
SUBJECTS = ["Mathematics","Science","Social Science","English","Hindi"]
CHAPTERS = {
    "Mathematics": ["Real Numbers","Polynomials","Pair of Linear Equations"],
    "Science": ["Chemical Reactions and Equations","Life Processes"],
    "Social Science": ["Nationalism in India","Political Parties"],
    "English": ["A Letter to God","Nelson Mandela"],
    "Hindi": ["सूरदास","आत्मकथ्य"]
}

# ======================================================
# DASHBOARD
# ======================================================
if st.session_state.page == "Dashboard":

    st.markdown("<div class='header'>📘 CBSE Grade 10 Smart Tutor</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"<div class='metric-box'><h3>⭐ XP</h3><h2>{st.session_state.xp}</h2></div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='metric-box'><h3>📖 Topics</h3><h2>{len(st.session_state.topic_history)}</h2></div>", unsafe_allow_html=True)

# ======================================================
# STUDY MODE
# ======================================================
elif st.session_state.page == "Study":

    st.markdown("## 📚 Study Mode")

    subject = st.selectbox("Subject", SUBJECTS)
    chapter = st.selectbox("Select Chapter", CHAPTERS.get(subject, []))

    mode = st.radio("Learning Mode", [
        "Concept Clarity",
        "Exam-Oriented Answers",
        "Previous Year Questions"
    ])

    if st.button("Generate", disabled=st.session_state.is_generating):
        st.session_state.is_generating = True
        st.session_state.generated_content = None
        st.rerun()

    if st.session_state.is_generating:

        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            with st.spinner("Generating Lesson..."):

                if subject == "Hindi":
                    prompt = f"कक्षा 10 CBSE विषय {subject}, अध्याय {chapter}, मोड {mode}. उत्तर हिंदी में दें।"
                else:
                    prompt = f"CBSE Grade 10 Subject {subject}, Chapter {chapter}, Mode {mode}. Follow NCERT structure."

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a CBSE evaluator."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )

                st.session_state.generated_content = response.choices[0].message.content
                st.session_state.xp += 20
                st.session_state.topic_history.append((subject, chapter))

        st.session_state.is_generating = False
        st.rerun()

    if st.session_state.generated_content:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(st.session_state.generated_content)
        st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# EXAM SIMULATION
# ======================================================
elif st.session_state.page == "Papers":

    st.markdown("## 📜 Exam Simulation")

    subject = st.selectbox("Subject", SUBJECTS)

    if st.button("Generate Paper"):
        with st.spinner("Generating Question Paper..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an official CBSE paper setter."},
                    {"role": "user", "content": f"Generate full paper for {subject} Class 10."}
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

    question = st.text_area("Ask your doubt")

    if st.button("Solve") and question:
        with st.spinner("Solving..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a CBSE teacher."},
                    {"role": "user", "content": question}
                ],
                temperature=0.2
            )

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write(response.choices[0].message.content)
            st.markdown("</div>", unsafe_allow_html=True)
