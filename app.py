import streamlit as st
from openai import OpenAI

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Grade 10 CBSE AI Tutor", layout="wide")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# =========================
# SESSION STATE INIT
# =========================
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "topic_history" not in st.session_state:
    st.session_state.topic_history = []
if "generating" not in st.session_state:
    st.session_state.generating = False
if "content_generated" not in st.session_state:
    st.session_state.content_generated = False

# =========================
# SUBJECTS & CHAPTERS
# =========================
SUBJECTS = {
    "Mathematics": ["Real Numbers", "Polynomials", "Quadratic Equations", "Arithmetic Progressions",
                    "Triangles", "Trigonometry", "Coordinate Geometry", "Statistics", "Probability"],

    "Science": ["Chemical Reactions", "Acids Bases Salts", "Metals and Non Metals",
                "Life Processes", "Control and Coordination", "Heredity and Evolution",
                "Light Reflection", "Human Eye", "Electricity", "Magnetic Effects"],

    "Social Science": ["Nationalism in Europe", "Nationalism in India",
                       "Resources and Development", "Water Resources",
                       "Power Sharing", "Federalism",
                       "Development", "Money and Credit"],

    "English": ["A Letter to God", "Nelson Mandela", "Two Stories about Flying",
                "From the Diary of Anne Frank"],

    "Hindi": ["सूरदास के पद", "राम-लक्ष्मण-परशुराम संवाद",
              "डायरी का एक पन्ना", "पतझर में टूटी पत्तियाँ"],

    "AI": ["Introduction to AI", "AI Project Cycle", "Neural Networks"],

    "IT": ["Digital Documentation", "Electronic Spreadsheet", "Database Management"]
}

# =========================
# SYSTEM ROLE
# =========================
def get_system_role(subject):
    if subject == "Hindi":
        return "You are a CBSE Hindi academic expert. All responses must be strictly in Hindi (Devanagari script only). Do NOT use English."
    return "You are a CBSE Grade 10 academic expert strictly aligned to NCERT and CBSE latest paper pattern."

# =========================
# PROMPT BUILDERS
# =========================
def build_study_prompt(subject, chapter):
    return f"""
Generate a COMPLETE structured lesson for Class 10 CBSE.

Subject: {subject}
Chapter: {chapter}

Structure:
1. Background
2. Key Concepts
3. Important Dates
4. Important People
5. Important Places
6. Key Definitions
7. Cause and Effect
8. Exam-Oriented Important Points
9. 5 Likely Board Questions
10. 5 MCQs with answers
11. 3 Assertion-Reason Questions
12. Quick Revision Sheet

Strictly follow NCERT syllabus only.
"""

def build_exam_prompt(subject):
    return f"""
Generate a FULL CBSE Class 10 Board Pattern Question Paper.

Subject: {subject}

Follow this structure:

Time: 3 Hours
Maximum Marks: 80

Section A: 1x20 MCQs
Section B: 2x6
Section C: 3x8
Section D: 4x5
Section E: Case Study Based (5 Marks)

Include internal choices.
Strictly NCERT based.
Minimum 40% competency based questions.
"""

# =========================
# GENERATE FUNCTION
# =========================
def generate_content(system_role, user_prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📘 Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Study", "Exam Simulator", "Previous Year Papers"])

# =========================
# DASHBOARD
# =========================
if page == "Dashboard":
    st.title("🎓 Grade 10 CBSE AI Tutor")

    level = st.session_state.xp // 100 + 1
    st.metric("⭐ XP Points", st.session_state.xp)
    st.metric("📈 Level", level)

# =========================
# STUDY PAGE
# =========================
elif page == "Study":

    st.title("📚 Study Mode")

    subject = st.selectbox("Select Subject", list(SUBJECTS.keys()))
    chapter = st.selectbox("Select Chapter", SUBJECTS[subject])

    if st.button("Generate", disabled=st.session_state.generating):

        st.session_state.generating = True
        st.session_state.content_generated = False
        st.rerun()

    if st.session_state.generating:

        with st.spinner("⏳ Generating Lesson..."):
            system_role = get_system_role(subject)
            prompt = build_study_prompt(subject, chapter)

            content = generate_content(system_role, prompt)

            st.session_state.generating = False
            st.session_state.content_generated = True

            if (subject, chapter) not in st.session_state.topic_history:
                st.session_state.topic_history.append((subject, chapter))
                st.session_state.xp += 10

            st.markdown(content)
            st.rerun()

# =========================
# EXAM SIMULATOR
# =========================
elif page == "Exam Simulator":

    st.title("📝 Exam Simulator")

    subject = st.selectbox("Select Subject", list(SUBJECTS.keys()))

    if st.button("Generate Exam Paper", disabled=st.session_state.generating):

        st.session_state.generating = True
        st.rerun()

    if st.session_state.generating:

        with st.spinner("⏳ Generating Exam Paper..."):
            system_role = get_system_role(subject)
            prompt = build_exam_prompt(subject)

            content = generate_content(system_role, prompt)

            st.session_state.generating = False
            st.markdown(content)
            st.rerun()

# =========================
# PREVIOUS YEAR PAPERS
# =========================
elif page == "Previous Year Papers":

    st.title("📄 Previous Year Papers")

    subject = st.selectbox("Select Subject", list(SUBJECTS.keys()))

    if st.button("Generate Previous Year Style Paper", disabled=st.session_state.generating):

        st.session_state.generating = True
        st.rerun()

    if st.session_state.generating:

        with st.spinner("⏳ Generating Paper..."):
            system_role = get_system_role(subject)
            prompt = build_exam_prompt(subject) + "\nSimulate realistic previous year board paper."

            content = generate_content(system_role, prompt)

            st.session_state.generating = False
            st.markdown(content)
            st.rerun()
