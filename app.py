import streamlit as st
from openai import OpenAI

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="CBSE Grade 10 AI Tutor", layout="wide")

# -------------------- OPENAI CLIENT --------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: 36px;
    font-weight: bold;
    color: #2E86C1;
}
.center-loader {
    text-align: center;
    font-size: 22px;
    font-weight: bold;
    margin-top: 30px;
}
.stButton > button {
    background-color: #2E86C1;
    color: white;
    font-size: 18px;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
.stButton > button:disabled {
    background-color: #A9CCE3;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>CBSE Grade 10 AI Academic Assistant</div>", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Select Option",
    [
        "Structured Lesson",
        "Exam Simulator",
        "Previous Years Papers",
        "Answer Evaluation"
    ]
)

# -------------------- SUBJECTS --------------------
subjects = {
    "Mathematics (Standard - 041)": [
        "Real Numbers",
        "Polynomials",
        "Pair of Linear Equations in Two Variables",
        "Quadratic Equations",
        "Arithmetic Progressions",
        "Triangles",
        "Coordinate Geometry",
        "Trigonometry",
        "Statistics",
        "Probability"
    ],
    "Science": [
        "Chemical Reactions",
        "Acids Bases and Salts",
        "Metals and Non Metals",
        "Life Processes",
        "Control and Coordination",
        "Electricity",
        "Light",
        "Our Environment"
    ],
    "Social Science - History": [
        "The Rise of Nationalism in Europe",
        "Nationalism in India",
        "The Making of a Global World",
        "The Age of Industrialisation"
    ],
    "English Language & Literature": [
        "First Flight",
        "Footprints Without Feet",
        "Grammar",
        "Writing Skills"
    ],
    "Hindi Course A": [
        "स्पर्श",
        "संचयन",
        "व्याकरण",
        "लेखन कौशल"
    ],
    "AI",
    "IT"
}

# -------------------- COMMON PROMPT --------------------
base_prompt = """
You are a CBSE Grade 10 academic expert strictly aligned with NCERT curriculum under CBSE guidelines.

Rules:
1. Follow latest CBSE pattern.
2. Minimum 40% competency-based.
3. Strictly NCERT.
4. Maintain board-level structure.
"""

# =========================================================
# =============== STRUCTURED LESSON =======================
# =========================================================
if menu == "Structured Lesson":

    subject = st.selectbox("Select Subject", list(subjects.keys()))

    chapter = None
    if isinstance(subjects[subject], list):
        chapter = st.selectbox("Select Chapter", subjects[subject])

    if st.button("Generate"):

        st.markdown("<div class='center-loader'>⏳ Generating Lesson...</div>", unsafe_allow_html=True)

        if "Hindi" in subject:
            language_instruction = "Generate full response strictly in Hindi language."
        else:
            language_instruction = "Generate response in English."

        prompt = f"""
        {base_prompt}

        {language_instruction}

        Provide structured lesson for:
        Subject: {subject}
        Chapter: {chapter}

        Include:
        - Background
        - Key Concepts
        - Important Dates
        - Important People
        - Important Places
        - Definitions
        - Cause & Effect
        - 5 Board Questions
        - 5 MCQs
        - 3 Assertion Reason
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        st.markdown(response.choices[0].message.content)

# =========================================================
# ================= EXAM SIMULATOR ========================
# =========================================================
elif menu == "Exam Simulator":

    subject = st.selectbox("Subject", list(subjects.keys()))
    scope = st.radio("Syllabus Scope", ["Chapter-wise", "Full Syllabus"])
    marks = st.selectbox("Marks", [30, 50, 80])
    difficulty = st.selectbox("Difficulty", ["Standard Board Level", "Slightly Tough"])

    if st.button("Generate Exam Paper"):

        st.markdown("<div class='center-loader'>⏳ Generating Question Paper...</div>", unsafe_allow_html=True)

        if "Hindi" in subject:
            language_instruction = "Generate complete question paper strictly in Hindi."
        else:
            language_instruction = "Generate paper in English."

        prompt = f"""
        {base_prompt}

        {language_instruction}

        Create a {marks} marks CBSE Grade 10 paper.
        Subject: {subject}
        Scope: {scope}
        Difficulty: {difficulty}

        Include:
        - General Instructions
        - Sections (MCQ, 2m, 3m, 4m, Case Study)
        - Internal choices
        - Time Duration
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        st.markdown(response.choices[0].message.content)

# =========================================================
# =============== PREVIOUS YEARS PAPERS ===================
# =========================================================
elif menu == "Previous Years Papers":

    st.subheader("📄 Previous Years Question Papers")

    subject = st.selectbox("Select Subject", list(subjects.keys()))
    year = st.selectbox("Select Year", ["2023", "2022", "2021", "2020", "2019"])

    if st.button("Generate Previous Year Paper"):

        st.markdown("<div class='center-loader'>⏳ Generating Previous Year Paper...</div>", unsafe_allow_html=True)

        if "Hindi" in subject:
            language_instruction = "Generate paper strictly in Hindi."
        else:
            language_instruction = "Generate paper in English."

        prompt = f"""
        {base_prompt}

        {language_instruction}

        Simulate CBSE Grade 10 {subject} Board Exam Paper for Year {year}.
        Follow authentic blueprint.
        Include internal choices.
        Maintain realistic difficulty.
        Include sections and marking scheme.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        st.markdown(response.choices[0].message.content)

# =========================================================
# ================= ANSWER EVALUATION =====================
# =========================================================
elif menu == "Answer Evaluation":

    subject = st.selectbox("Subject", list(subjects.keys()))
    question = st.text_area("Paste Question")
    answer = st.text_area("Paste Student Answer")

    if st.button("Evaluate"):

        st.markdown("<div class='center-loader'>⏳ Evaluating...</div>", unsafe_allow_html=True)

        prompt = f"""
        {base_prompt}

        Evaluate answer with step marking.
        Classify mistakes:
        - Concept
        - Formula
        - Calculation
        - Presentation
        - Interpretation

        Question:
        {question}

        Answer:
        {answer}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        st.markdown(response.choices[0].message.content)
