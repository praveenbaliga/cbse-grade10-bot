import streamlit as st
from openai import OpenAI

# ==============================
# CONFIG
# ==============================
st.set_page_config(
    page_title="CBSE Grade 10 Smart Tutor",
    page_icon="📘",
    layout="wide"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==============================
# MODERN CLEAN UI
# ==============================
st.markdown("""
<style>

.main {
    background-color: #f8fafc;
}

.header-title {
    font-size: 38px;
    font-weight: 700;
    color: #111827;
}

.subtitle {
    font-size: 18px;
    color: #6b7280;
    margin-bottom: 30px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    height: 3em;
    font-size: 16px;
    border: none;
    width: 100%;
}

.stSelectbox label {
    font-weight: 600;
}

.metric-box {
    background: white;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
student_name = "Student"  # change name

st.markdown(f"<div class='header-title'>📘 Welcome {student_name}</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your Personal CBSE Grade 10 Learning Dashboard</div>", unsafe_allow_html=True)

# ==============================
# XP + STREAK (Subtle Gamification)
# ==============================
if "xp" not in st.session_state:
    st.session_state.xp = 0

if "streak" not in st.session_state:
    st.session_state.streak = 1

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"<div class='metric-box'><h3>⭐ XP</h3><h2>{st.session_state.xp}</h2></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='metric-box'><h3>🔥 Streak</h3><h2>{st.session_state.streak} days</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# ==============================
# SUBJECT GRID
# ==============================
st.markdown("## 📚 Select Subject")

subjects = [
    "Mathematics",
    "Science",
    "Social Science",
    "English",
    "Hindi A",
    "Hindi B",
    "Artificial Intelligence",
    "Information Technology"
]

cols = st.columns(4)

for i, subject in enumerate(subjects):
    with cols[i % 4]:
        if st.button(subject):
            st.session_state.subject = subject

# ==============================
# SYLLABUS
# ==============================
CBSE_SYLLABUS = {
    "Mathematics": ["Real Numbers", "Polynomials", "Quadratic Equations", "Trigonometry", "Statistics", "Probability"],
    "Science": ["Chemical Reactions", "Life Processes", "Electricity", "Light"],
    "Social Science": ["Nationalism in India", "Federalism", "Democracy"],
    "English": ["Prose", "Poetry", "Writing Skills", "Grammar"],
    "Hindi A": ["गद्य", "पद्य", "व्याकरण", "लेखन कौशल"],
    "Hindi B": ["गद्य", "पद्य", "व्याकरण", "लेखन"],
    "Artificial Intelligence": ["Introduction to AI", "AI Project Cycle", "Data Literacy", "Python Basics"],
    "Information Technology": ["Digital Documentation", "Electronic Spreadsheet", "Database Management"]
}

# ==============================
# CHAPTER + MODE
# ==============================
if "subject" in st.session_state:

    st.markdown(f"## 📖 {st.session_state.subject}")

    chapter = st.selectbox(
        "Choose Chapter",
        CBSE_SYLLABUS[st.session_state.subject]
    )

    mode = st.radio(
        "Select Mode",
        ["Chapter Summary", "Important Questions", "Practice Test"]
    )

    if st.button("Generate Lesson"):

        with st.spinner("Preparing lesson..."):

            prompt = f"""
            You are an expert CBSE Grade 10 teacher.
            Subject: {st.session_state.subject}
            Chapter: {chapter}
            Mode: {mode}

            Follow CBSE 2026 pattern.
            Provide structured content with headings.
            Include examples and exam-oriented questions.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional CBSE teacher."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )

            output = response.choices[0].message.content

        st.session_state.xp += 20

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Lesson Output")
        st.write(output)
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# DOUBT SOLVER
# ==============================
st.markdown("---")
st.markdown("## 💬 Ask a Doubt")

question = st.text_input("Type your question")

if st.button("Get Answer") and question:

    with st.spinner("Thinking..."):

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a CBSE Grade 10 teacher."},
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
<div style='text-align:center; padding:20px; color:#9ca3af; font-size:14px;'>
CBSE 2026 Pattern | Clean Learning Experience
</div>
""", unsafe_allow_html=True)
