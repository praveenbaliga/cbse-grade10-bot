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
    margin-top: 20px;
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
# SIDEBAR
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
    "Mathematics", "Science", "Social Science",
    "English", "Hindi",
    "Artificial Intelligence", "Information Technology"
]

YEARS = ["2024", "2023", "2022", "2021", "2020"]

CHAPTERS = {
    "Mathematics": ["Real Numbers","Polynomials","Pair of Linear Equations",
                    "Quadratic Equations","Arithmetic Progressions",
                    "Triangles","Coordinate Geometry","Trigonometry",
                    "Mensuration","Statistics","Probability"],
    "Science": ["Chemical Reactions and Equations","Acids Bases and Salts",
                "Metals and Non-metals","Life Processes",
                "Control and Coordination","How do Organisms Reproduce",
                "Heredity and Evolution","Light Reflection and Refraction",
                "Human Eye and the Colourful World","Sources of Energy"],
    "Social Science": ["Nationalism in Europe","Nationalism in India",
                       "Resources and Development","Agriculture",
                       "Manufacturing Industries","Political Parties",
                       "Outcomes of Democracy"],
    "English": ["A Letter to God","Nelson Mandela",
                "Two Stories About Flying","From the Diary of Anne Frank"],
    "Hindi": ["सूरदास","राम-लक्ष्मण-परशुराम संवाद","आत्मकथ्य","पद"],
    "Artificial Intelligence": ["AI Project Cycle","Neural Networks"],
    "Information Technology": ["Digital Documentation","Electronic Spreadsheet"]
}

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
        "Competency Case Study",
        "Practice Test (40 Marks)",
        "Previous Year Questions"
    ])

    # GENERATE BUTTON
    if st.button("Generate", disabled=st.session_state.is_generating):

        st.session_state.is_generating = True
        st.session_state.generated_content = None

        # Centered Loader
        with st.container():
            c1, c2, c3 = st.columns([1,2,1])
            with c2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                with st.spinner("Generating..."):
                    
                    # Prompt Creation
                    if subject == "Hindi":
                        prompt = f"""
आप एक सख्त CBSE कक्षा 10 शिक्षक हैं।

विषय: {subject}
अध्याय: {chapter}
मोड: {mode}

उत्तर पूरी तरह हिंदी में दें।
NCERT आधारित संरचना:

### 📘 अवधारणा
### 🧠 मुख्य बिंदु
### ✏ उदाहरण
### 🎯 परीक्षा टिप
### ❓ अभ्यास प्रश्न
### ✅ उत्तर
"""
                    else:
                        prompt = f"""
You are a strict CBSE Grade 10 teacher aligned to NCERT.

Subject: {subject}
Chapter: {chapter}
Mode: {mode}

Structure:
### 📘 Concept Explanation
### 🧠 Key Points
### ✏ Step-by-Step Example
### 🎯 Exam Tip
### ❓ Practice Questions
### ✅ Answers
"""

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a precise CBSE evaluator."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3
                    )

                    st.session_state.generated_content = response.choices[0].message.content
                    st.session_state.xp += 20
                    st.session_state.topic_history.append((subject, chapter))

        st.session_state.is_generating = False
        st.rerun()

    # DISPLAY CONTENT
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
    year = st.selectbox("Pattern Year", YEARS)

    if st.button("Generate Paper"):

        with st.spinner("Generating Question Paper..."):

            prompt = f"Generate CBSE Grade 10 {subject} paper based on {year} blueprint."

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

    question = st.text_area("Ask your doubt")

    if st.button("Solve") and question:

        with st.spinner("Solving..."):

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a precise CBSE teacher."},
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
CBSE Blueprint Aligned | 90+ Strategy Mode
</div>
""", unsafe_allow_html=True)
