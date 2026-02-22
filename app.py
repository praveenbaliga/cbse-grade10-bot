import streamlit as st
from openai import OpenAI

# ===============================
# CONFIG
# ===============================
st.set_page_config(
    page_title="CBSE Grade 10 Smart Tutor",
    page_icon="📘",
    layout="wide"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ===============================
# SESSION STATE INIT
# ===============================
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "xp" not in st.session_state:
    st.session_state.xp = 0

# ===============================
# UI STYLING
# ===============================
st.markdown("""
<style>
.main { background-color: #f8fafc; }

.header { font-size: 34px; font-weight: 700; color: #111827; }

.card {
    background: white;
    padding: 20px;
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
</style>
""", unsafe_allow_html=True)

# ===============================
# SIDEBAR NAVIGATION
# ===============================
st.sidebar.title("Navigation")

if st.sidebar.button("🏠 Dashboard"):
    st.session_state.page = "Dashboard"

if st.sidebar.button("📚 Study Mode"):
    st.session_state.page = "Study"

if st.sidebar.button("📜 Previous Year Papers"):
    st.session_state.page = "Papers"

if st.sidebar.button("💬 Doubt Solver"):
    st.session_state.page = "Doubt"

# ===============================
# SUBJECT DATA
# ===============================
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

# ===============================
# DASHBOARD
# ===============================
if st.session_state.page == "Dashboard":

    st.markdown("<div class='header'>📘 CBSE Grade 10 Smart Tutor</div>", unsafe_allow_html=True)
    st.markdown("### ⭐ XP:", st.session_state.xp)

    st.markdown("---")
    st.markdown("## Select Subject")

    cols = st.columns(4)

    for i, subject in enumerate(SUBJECTS):
        with cols[i % 4]:
            if st.button(subject):
                st.session_state.selected_subject = subject
                st.session_state.page = "Study"

# ===============================
# STUDY MODE
# ===============================
elif st.session_state.page == "Study":

    st.markdown("## 📚 Study Mode")

    subject = st.selectbox("Subject", SUBJECTS)
    chapter = st.text_input("Enter Chapter Name")
    mode = st.radio("Mode", ["Summary", "Important Questions", "Practice Test"])

    if st.button("Generate Content"):

        prompt = f"""
        You are a strict CBSE Grade 10 teacher.
        Follow NCERT syllabus.
        Subject: {subject}
        Chapter: {chapter}
        Mode: {mode}

        Use structured headings.
        Show formulas if applicable.
        Follow CBSE 2026 exam pattern.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert CBSE teacher."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        st.session_state.xp += 20

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(response.choices[0].message.content)
        st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# PREVIOUS YEAR PAPERS
# ===============================
elif st.session_state.page == "Papers":

    st.markdown("## 📜 Previous Year Papers")

    subject = st.selectbox("Subject", SUBJECTS)
    year = st.selectbox("Year", YEARS)

    if st.button("Generate Sample Paper Based on Year"):

        prompt = f"""
        Generate a CBSE Grade 10 {subject} question paper
        based on {year} CBSE pattern.
        Include:
        - Section A MCQs
        - Section B Short Answer
        - Section C Long Answer
        Follow authentic CBSE blueprint.
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

# ===============================
# DOUBT SOLVER
# ===============================
elif st.session_state.page == "Doubt":

    st.markdown("## 💬 Doubt Solver")

    question = st.text_area("Ask your doubt")

    if st.button("Solve Doubt"):

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise CBSE teacher. Provide accurate answers only."},
                {"role": "user", "content": question}
            ],
            temperature=0.2
        )

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(response.choices[0].message.content)
        st.markdown("</div>", unsafe_allow_html=True)
