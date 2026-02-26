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
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');

/* ---- ROOT VARIABLES ---- */
:root {
    --bg: #0f1117;
    --surface: #1a1d2e;
    --surface2: #222640;
    --accent1: #6c63ff;
    --accent2: #f97316;
    --accent3: #22d3ee;
    --accent4: #a78bfa;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --success: #4ade80;
    --danger: #f87171;
    --border: rgba(108,99,255,0.18);
    --radius: 16px;
    --glow: 0 0 24px rgba(108,99,255,0.25);
}

/* ---- GLOBAL ---- */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.main .block-container {
    background-color: var(--bg);
    padding: 2rem 2.5rem;
}

/* ---- ANIMATED BACKGROUND GRID ---- */
.main::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(108,99,255,0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(108,99,255,0.05) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* ---- SIDEBAR ---- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12152b 0%, #1a1d35 100%) !important;
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--muted) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em;
    transition: all 0.25s ease !important;
    margin-bottom: 6px;
    text-align: left !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(90deg, rgba(108,99,255,0.2), rgba(167,139,250,0.1)) !important;
    border-color: var(--accent1) !important;
    color: var(--text) !important;
    transform: translateX(4px);
    box-shadow: var(--glow);
}

/* ---- PAGE HEADER ---- */
.page-header {
    font-size: 2.2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #6c63ff, #a78bfa, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
    letter-spacing: -0.02em;
}

.page-sub {
    color: var(--muted);
    font-size: 0.95rem;
    margin-bottom: 2rem;
    font-weight: 600;
}

/* ---- METRIC CARDS ---- */
.metric-card {
    background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px 28px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: var(--radius) var(--radius) 0 0;
}

.metric-card.xp::before { background: linear-gradient(90deg, #6c63ff, #a78bfa); }
.metric-card.topics::before { background: linear-gradient(90deg, #22d3ee, #4ade80); }
.metric-card.streak::before { background: linear-gradient(90deg, #f97316, #fbbf24); }

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(108,99,255,0.2);
}

.metric-icon {
    font-size: 2.2rem;
    margin-bottom: 8px;
}

.metric-label {
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 6px;
}

.metric-value {
    font-size: 2.4rem;
    font-weight: 900;
    color: var(--text);
    font-family: 'Space Mono', monospace;
    line-height: 1;
}

/* ---- QUICK TILES ---- */
.quick-tile {
    background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 22px;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
}

.quick-tile:hover {
    transform: translateY(-3px);
    border-color: var(--accent1);
    box-shadow: var(--glow);
}

.quick-tile-icon { font-size: 2rem; margin-bottom: 10px; }
.quick-tile-title { font-weight: 800; font-size: 1rem; color: var(--text); margin-bottom: 4px; }
.quick-tile-desc { font-size: 0.82rem; color: var(--muted); font-weight: 600; }

/* ---- CONTENT CARD ---- */
.content-card {
    background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px 32px;
    margin-top: 20px;
    position: relative;
}

.content-card::before {
    content: '✨ AI Response';
    position: absolute;
    top: -12px;
    left: 20px;
    background: linear-gradient(90deg, var(--accent1), var(--accent4));
    color: white;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    padding: 4px 12px;
    border-radius: 20px;
    text-transform: uppercase;
}

/* ---- SELECTBOXES & INPUTS ---- */
.stSelectbox > div > div {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
}

.stSelectbox > div > div:hover {
    border-color: var(--accent1) !important;
}

.stTextArea > div > textarea {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.95rem;
}

.stTextArea > div > textarea:focus {
    border-color: var(--accent1) !important;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.2) !important;
}

/* ---- RADIO BUTTONS ---- */
.stRadio > div {
    gap: 10px !important;
}

.stRadio label {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}

.stRadio label:hover {
    border-color: var(--accent1) !important;
    background: var(--surface2) !important;
}

/* ---- MAIN BUTTONS ---- */
.stButton > button {
    background: linear-gradient(90deg, var(--accent1), var(--accent4)) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    height: 3.2em !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    font-family: 'Nunito', sans-serif !important;
    letter-spacing: 0.04em;
    transition: all 0.25s !important;
    box-shadow: 0 4px 15px rgba(108,99,255,0.35) !important;
    width: 100%;
}

.stButton > button:hover:not(:disabled) {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(108,99,255,0.5) !important;
}

.stButton > button:disabled {
    background: var(--surface2) !important;
    color: var(--muted) !important;
    box-shadow: none !important;
}

/* ---- LABELS ---- */
.stSelectbox label, .stTextArea label, .stRadio label p {
    color: var(--muted) !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ---- SECTION DIVIDER ---- */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 32px 0 18px 0;
}

.section-header-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border), transparent);
}

.section-header-text {
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    white-space: nowrap;
}

/* ---- XP BADGE ---- */
.xp-badge {
    display: inline-block;
    background: linear-gradient(90deg, var(--accent1), var(--accent4));
    color: white;
    font-size: 0.72rem;
    font-weight: 800;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ---- HISTORY PILLS ---- */
.history-pill {
    display: inline-block;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--muted);
    margin: 3px;
}

/* ---- SPINNER FIX ---- */
.stSpinner > div {
    border-top-color: var(--accent1) !important;
}

/* ---- SCROLLBAR ---- */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent1); }

/* ---- SIDEBAR TITLE ---- */
section[data-testid="stSidebar"] h1 {
    font-size: 1rem !important;
    font-weight: 900 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    margin-bottom: 16px !important;
}

/* ---- ALERT BOX ---- */
.stAlert {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
}

/* ---- MARKDOWN CONTENT ---- */
.content-card p, .content-card li, .content-card h1, .content-card h2, .content-card h3 {
    color: var(--text) !important;
}

.content-card h2, .content-card h3 {
    color: var(--accent4) !important;
}

/* ---- WATERMARK ---- */
.sidebar-watermark {
    position: fixed;
    bottom: 20px;
    left: 0;
    width: 260px;
    text-align: center;
    font-size: 0.72rem;
    color: var(--muted);
    font-weight: 700;
    letter-spacing: 0.06em;
    opacity: 0.5;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR NAVIGATION
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

    if st.button("💬  Doubt Solver"):
        st.session_state.page = "Doubt"

    st.markdown("---")

    # XP Progress in sidebar
    level = st.session_state.xp // 100 + 1
    xp_in_level = st.session_state.xp % 100
    st.markdown(f"""
    <div style='padding: 14px; background: rgba(108,99,255,0.1); border-radius: 12px; border: 1px solid rgba(108,99,255,0.2);'>
        <div style='font-size:0.72rem; font-weight:800; letter-spacing:0.08em; color:#94a3b8; text-transform:uppercase; margin-bottom:6px;'>Level {level} Scholar</div>
        <div style='font-size:1.5rem; font-weight:900; color:#e2e8f0; font-family: Space Mono, monospace;'>⭐ {st.session_state.xp} XP</div>
        <div style='margin-top:10px; background:rgba(255,255,255,0.08); border-radius:20px; height:6px; overflow:hidden;'>
            <div style='height:100%; width:{xp_in_level}%; background:linear-gradient(90deg,#6c63ff,#a78bfa); border-radius:20px; transition:width 0.5s;'></div>
        </div>
        <div style='font-size:0.7rem; color:#94a3b8; margin-top:4px; font-weight:600;'>{xp_in_level}/100 to next level</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div class='sidebar-watermark'>CBSE Grade 10 · 2024–25</div>", unsafe_allow_html=True)


# ======================================================
# DATA
# ======================================================
SUBJECTS = ["Mathematics", "Science", "Social Science", "English", "Hindi", "Artificial Intelligence", "Information Technology"]
CHAPTERS = {
    "Mathematics": [
        "Real Numbers",
        "Polynomials",
        "Pair of Linear Equations in Two Variables",
        "Quadratic Equations",
        "Arithmetic Progressions",
        "Triangles",
        "Coordinate Geometry",
        "Introduction to Trigonometry",
        "Some Applications of Trigonometry",
        "Circles",
        "Areas Related to Circles",
        "Surface Areas and Volumes",
        "Statistics",
        "Probability"
    ],
    "Science": [
        "Chemical Reactions and Equations",
        "Acids, Bases and Salts",
        "Metals and Non-metals",
        "Carbon and its Compounds",
        "Life Processes",
        "Control and Coordination",
        "How do Organisms Reproduce?",
        "Heredity",
        "Light – Reflection and Refraction",
        "The Human Eye and the Colourful World",
        "Electricity",
        "Magnetic Effects of Electric Current",
        "Our Environment"
    ],
    "Social Science": [
        "The Rise of Nationalism in Europe",
        "Nationalism in India",
        "The Making of a Global World",
        "The Age of Industrialisation",
        "Print Culture and the Modern World",
        "Resources and Development",
        "Forest and Wildlife Resources",
        "Water Resources",
        "Agriculture",
        "Minerals and Energy Resources",
        "Manufacturing Industries",
        "Lifelines of National Economy",
        "Power Sharing",
        "Federalism",
        "Gender, Religion and Caste",
        "Political Parties",
        "Outcomes of Democracy",
        "Development",
        "Sectors of the Indian Economy",
        "Money and Credit",
        "Globalisation and the Indian Economy",
        "Consumer Rights"
    ],
    "English": [
        "A Letter to God",
        "Nelson Mandela: Long Walk to Freedom",
        "Two Stories about Flying",
        "From the Diary of Anne Frank",
        "Glimpses of India",
        "Mijbil the Otter",
        "Madam Rides the Bus",
        "The Sermon at Benares",
        "The Proposal",
        "A Triumph of Surgery",
        "The Thief's Story",
        "The Midnight Visitor",
        "A Question of Trust",
        "Footprints without Feet",
        "The Making of a Scientist",
        "The Necklace",
        "Bholi",
        "The Book That Saved the Earth"
    ],
    "Hindi": [
        "सूरदास — पद",
        "तुलसीदास — राम-लक्ष्मण-परशुराम संवाद",
        "देव — सवैया और कवित्त",
        "जयशंकर प्रसाद — आत्मकथ्य",
        "सूर्यकांत त्रिपाठी 'निराला' — उत्साह और अट नहीं रही",
        "नागार्जुन — यह दंतुरहित मुस्कान और फसल",
        "गिरिजाकुमार माथुर — छाया मत छूना",
        "ऋतुराज — कन्यादान",
        "मंगलेश डबराल — संगतकार",
        "स्वयं प्रकाश — नेताजी का चश्मा",
        "रामवृक्ष बेनीपुरी — बालगोबिन भगत",
        "यशपाल — लखनवी अंदाज़",
        "सर्वेश्वर दयाल सक्सेना — मानवीय करुणा की दिव्य चमक",
        "मन्नू भंडारी — एक कहानी यह भी",
        "महावीर प्रसाद द्विवेदी — स्त्री शिक्षा के विरोधी कुतर्कों का खंडन",
        "यतींद्र मिश्र — नौबतखाने में इबादत",
        "भदंत आनंद कौसल्यायन — संस्कृति"
    ],
    "Artificial Intelligence": [
        "Introduction to Artificial Intelligence",
        "AI Project Cycle",
        "Problem Scoping",
        "Data Acquisition",
        "Data Exploration",
        "Modelling",
        "Evaluation",
        "Natural Language Processing (NLP)",
        "Computer Vision",
        "Machine Learning Basics",
        "Neural Networks and Deep Learning",
        "AI Ethics and Bias",
        "AI Applications in Society",
        "Future of AI and Emerging Trends"
    ],
    "Information Technology": [
        "Communication Skills",
        "Self-Management Skills",
        "ICT Skills",
        "Entrepreneurial Skills",
        "Green Skills",
        "Digital Documentation (Advanced) — LibreOffice Writer",
        "Electronic Spreadsheet (Advanced) — LibreOffice Calc",
        "Database Management System — LibreOffice Base",
        "Web Applications and Security",
        "HTML Basics and Structure",
        "Working with Tables and Forms in HTML",
        "Introduction to CSS",
        "Cyber Safety and Ethics",
        "E-Commerce and Digital Payments"
    ]
}

SUBJECT_COLORS = {
    "Mathematics": "#6c63ff",
    "Science": "#22d3ee",
    "Social Science": "#4ade80",
    "English": "#f97316",
    "Hindi": "#f472b6",
    "Artificial Intelligence": "#facc15",
    "Information Technology": "#818cf8",
}

SUBJECT_ICONS = {
    "Mathematics": "📐",
    "Science": "🔬",
    "Social Science": "🌍",
    "English": "📖",
    "Hindi": "✍️",
    "Artificial Intelligence": "🤖",
    "Information Technology": "💻",
}

# ======================================================
# DASHBOARD
# ======================================================
if st.session_state.page == "Dashboard":

    st.markdown("<div class='page-header'>📘 CBSE Smart Tutor</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Your AI-powered study companion for Grade 10</div>", unsafe_allow_html=True)

    # Metrics Row
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class='metric-card xp'>
            <div class='metric-icon'>⭐</div>
            <div class='metric-label'>Total XP Earned</div>
            <div class='metric-value'>{st.session_state.xp}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class='metric-card topics'>
            <div class='metric-icon'>📖</div>
            <div class='metric-label'>Topics Studied</div>
            <div class='metric-value'>{len(st.session_state.topic_history)}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        level = st.session_state.xp // 100 + 1
        st.markdown(f"""
        <div class='metric-card streak'>
            <div class='metric-icon'>🏆</div>
            <div class='metric-label'>Scholar Level</div>
            <div class='metric-value'>{level}</div>
        </div>
        """, unsafe_allow_html=True)

    # Quick Access
    st.markdown("""
    <div class='section-header'>
        <div class='section-header-text'>Quick Access</div>
        <div class='section-header-line'></div>
    </div>
    """, unsafe_allow_html=True)

    q1, q2, q3 = st.columns(3)

    with q1:
        st.markdown("""
        <div class='quick-tile'>
            <div class='quick-tile-icon'>📚</div>
            <div class='quick-tile-title'>Study Mode</div>
            <div class='quick-tile-desc'>NCERT-based concept explanations & PYQs</div>
        </div>
        """, unsafe_allow_html=True)

    with q2:
        st.markdown("""
        <div class='quick-tile'>
            <div class='quick-tile-icon'>📜</div>
            <div class='quick-tile-title'>Exam Simulation</div>
            <div class='quick-tile-desc'>Full-length CBSE-style question papers</div>
        </div>
        """, unsafe_allow_html=True)

    with q3:
        st.markdown("""
        <div class='quick-tile'>
            <div class='quick-tile-icon'>💬</div>
            <div class='quick-tile-title'>Doubt Solver</div>
            <div class='quick-tile-desc'>Get instant answers from your AI teacher</div>
        </div>
        """, unsafe_allow_html=True)

    # Subject progress tiles
    st.markdown("""
    <div class='section-header'>
        <div class='section-header-text'>Subjects</div>
        <div class='section-header-line'></div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(7)
    for i, subject in enumerate(SUBJECTS):
        count = sum(1 for s, _ in st.session_state.topic_history if s == subject)
        color = SUBJECT_COLORS[subject]
        icon = SUBJECT_ICONS[subject]
        with cols[i]:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#1a1d2e,#222640); border:1px solid {color}30;
                        border-radius:14px; padding:18px 14px; text-align:center; border-top: 3px solid {color};
                        transition: transform 0.2s;'>
                <div style='font-size:1.8rem; margin-bottom:8px;'>{icon}</div>
                <div style='font-size:0.78rem; font-weight:800; color:#e2e8f0;'>{subject}</div>
                <div style='font-size:1.4rem; font-weight:900; color:{color}; font-family:Space Mono,monospace; margin-top:4px;'>{count}</div>
                <div style='font-size:0.68rem; color:#64748b; font-weight:700;'>sessions</div>
            </div>
            """, unsafe_allow_html=True)

    # History
    if st.session_state.topic_history:
        st.markdown("""
        <div class='section-header'>
            <div class='section-header-text'>Recent Activity</div>
            <div class='section-header-line'></div>
        </div>
        """, unsafe_allow_html=True)
        pills_html = "".join([f"<span class='history-pill'>{SUBJECT_ICONS.get(s, '📘')} {s} · {ch}</span>"
                               for s, ch in reversed(st.session_state.topic_history[-10:])])
        st.markdown(f"<div style='line-height:2.5;'>{pills_html}</div>", unsafe_allow_html=True)


# ======================================================
# STUDY MODE
# ======================================================
elif st.session_state.page == "Study":

    st.markdown("<div class='page-header'>📚 Study Mode</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>NCERT-aligned lessons crafted just for you</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        subject = st.selectbox("🎯 Subject", SUBJECTS)
    with c2:
        chapter = st.selectbox("📌 Chapter", CHAPTERS.get(subject, []))

    st.markdown("<br>", unsafe_allow_html=True)
    mode = st.radio("📋 Learning Mode", [
        "Concept Clarity",
        "Exam-Oriented Answers",
        "Previous Year Questions"
    ], horizontal=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✨ Generate Lesson", disabled=st.session_state.is_generating):
        st.session_state.is_generating = True
        st.session_state.generated_content = None
        st.rerun()

    if st.session_state.is_generating:
        with st.spinner("🔮 Crafting your personalized lesson..."):
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
        color = SUBJECT_COLORS.get(subject, "#6c63ff")
        icon = SUBJECT_ICONS.get(subject, "📘")
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:12px; margin: 24px 0 8px 0;'>
            <span style='font-size:1.4rem;'>{icon}</span>
            <span style='font-weight:800; color:#e2e8f0; font-size:1rem;'>{subject} · {chapter}</span>
            <span style='background:linear-gradient(90deg,{color},{color}88); color:white; font-size:0.7rem;
                         font-weight:800; padding:3px 12px; border-radius:20px; text-transform:uppercase; letter-spacing:0.06em;'>{mode}</span>
            <span style='margin-left:auto;' class='xp-badge'>+20 XP</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.write(st.session_state.generated_content)
        st.markdown("</div>", unsafe_allow_html=True)


# ======================================================
# EXAM SIMULATION
# ======================================================
elif st.session_state.page == "Papers":

    st.markdown("<div class='page-header'>📜 Exam Simulation</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>CBSE-pattern full question papers, generated on demand</div>", unsafe_allow_html=True)

    subject = st.selectbox("🎯 Choose Subject", SUBJECTS)

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1a1d2e,#222640); border:1px solid {SUBJECT_COLORS.get(subject,"#6c63ff")}40;
                border-radius:14px; padding:20px 24px; margin: 16px 0; display:flex; gap:16px; align-items:center;'>
        <span style='font-size:2.5rem;'>{SUBJECT_ICONS.get(subject,"📘")}</span>
        <div>
            <div style='font-weight:800; font-size:1.1rem; color:#e2e8f0;'>{subject} — Class 10</div>
            <div style='font-size:0.82rem; color:#94a3b8; font-weight:600; margin-top:2px;'>
                Based on latest CBSE syllabus · NCERT pattern · 80 marks
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Generate Question Paper"):
        with st.spinner("📝 Setting your exam paper..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an official CBSE paper setter."},
                    {"role": "user", "content": f"Generate full paper for {subject} Class 10."}
                ],
                temperature=0.3
            )
            st.session_state.xp += 10

        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.write(response.choices[0].message.content)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<span class='xp-badge'>+10 XP Earned!</span>", unsafe_allow_html=True)


# ======================================================
# DOUBT SOLVER
# ======================================================
elif st.session_state.page == "Doubt":

    st.markdown("<div class='page-header'>💬 Doubt Solver</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Your AI teacher is ready — ask anything!</div>", unsafe_allow_html=True)

    # Example prompts
    st.markdown("""
    <div style='display:flex; gap:10px; flex-wrap:wrap; margin-bottom:20px;'>
        <span style='background:#1a1d2e; border:1px solid rgba(108,99,255,0.2); border-radius:20px; padding:6px 14px;
                     font-size:0.8rem; font-weight:700; color:#94a3b8;'>💡 Explain photosynthesis</span>
        <span style='background:#1a1d2e; border:1px solid rgba(108,99,255,0.2); border-radius:20px; padding:6px 14px;
                     font-size:0.8rem; font-weight:700; color:#94a3b8;'>💡 What is HCF?</span>
        <span style='background:#1a1d2e; border:1px solid rgba(108,99,255,0.2); border-radius:20px; padding:6px 14px;
                     font-size:0.8rem; font-weight:700; color:#94a3b8;'>💡 Causes of WW1</span>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_area("🤔 Your Question", placeholder="Type your doubt here... I'll explain it simply!", height=140)

    if st.button("🔍 Solve My Doubt") and question:
        with st.spinner("🧠 Thinking through your doubt..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a friendly, encouraging CBSE teacher who explains concepts clearly and simply."},
                    {"role": "user", "content": question}
                ],
                temperature=0.2
            )
            st.session_state.xp += 5

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1a1d2e,#222640); border:1px solid rgba(34,211,238,0.2);
                    border-radius:14px; padding:14px 18px; margin:16px 0; display:flex; gap:12px; align-items:flex-start;'>
            <span style='font-size:1.2rem;'>❓</span>
            <div style='font-weight:700; color:#94a3b8; font-size:0.9rem;'>{question[:200]}{"..." if len(question)>200 else ""}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.write(response.choices[0].message.content)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<span class='xp-badge'>+5 XP Earned!</span>", unsafe_allow_html=True)
