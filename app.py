import streamlit as st
from openai import OpenAI

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
if "exam_mode_default" not in st.session_state:
    st.session_state.exam_mode_default = "Full Question Paper (80 marks)"
if "mcq_questions" not in st.session_state:
    st.session_state.mcq_questions = None
if "mcq_answers" not in st.session_state:
    st.session_state.mcq_answers = {}
if "mcq_submitted" not in st.session_state:
    st.session_state.mcq_submitted = False
if "mcq_subject" not in st.session_state:
    st.session_state.mcq_subject = None
if "mcq_chapter" not in st.session_state:
    st.session_state.mcq_chapter = None

# ======================================================
# HANDLE MOBILE NAV QUERY PARAMS (must be before any render)
# ======================================================
_qp = st.query_params
if "nav" in _qp and _qp["nav"] in ["Dashboard", "Study", "Papers", "PYQ", "ChapTest", "MCQ", "Doubt"]:
    nav_dest = _qp["nav"]
    if nav_dest == "ChapTest":
        st.session_state.page = "Papers"
        st.session_state.exam_mode_default = "Chapter-Wise Practice Test"
    elif nav_dest == "MCQ":
        st.session_state.page = "Papers"
        st.session_state.exam_mode_default = "MCQ Quiz (Auto-Evaluated)"
    else:
        st.session_state.page = nav_dest
    st.query_params.clear()
    st.rerun()

# ======================================================
# STYLING
# ======================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');

/* ---- VARIABLES ---- */
:root {
    --bg: #0f1117;
    --surface: #1a1d2e;
    --surface2: #222640;
    --accent1: #6c63ff;
    --accent4: #a78bfa;
    --accent3: #22d3ee;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --border: rgba(108,99,255,0.18);
    --radius: 16px;
    --glow: 0 0 24px rgba(108,99,255,0.25);
}

/* ---- BASE ---- */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.main .block-container {
    background-color: var(--bg);
    padding: 1.2rem 1rem 1.5rem 1rem;
    max-width: 100% !important;
}
@media (min-width: 769px) {
    .main .block-container { padding: 2rem 2.5rem; }
}

/* Grid bg */
.main::before {
    content: '';
    position: fixed;
    inset: 0;
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
    min-width: 220px !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--muted) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
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
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2 {
    font-size: 1rem !important;
    font-weight: 900 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
.sidebar-watermark {
    text-align: center;
    font-size: 0.7rem;
    color: var(--muted);
    font-weight: 700;
    letter-spacing: 0.06em;
    opacity: 0.45;
    margin-top: 16px;
}

/* ---- PAGE HEADER ---- */
.page-header {
    font-size: clamp(1.5rem, 5vw, 2.2rem);
    font-weight: 900;
    background: linear-gradient(90deg, #6c63ff, #a78bfa, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.page-sub {
    color: var(--muted);
    font-size: clamp(0.82rem, 2.5vw, 0.95rem);
    margin-bottom: 1.5rem;
    font-weight: 600;
}

/* ---- METRICS GRID ---- */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 24px;
}
@media (max-width: 480px) {
    .metrics-grid { grid-template-columns: 1fr; gap: 10px; }
}
.metric-card {
    background: linear-gradient(135deg, var(--surface), var(--surface2));
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 16px;
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
.metric-card.xp::before     { background: linear-gradient(90deg, #6c63ff, #a78bfa); }
.metric-card.topics::before  { background: linear-gradient(90deg, #22d3ee, #4ade80); }
.metric-card.streak::before  { background: linear-gradient(90deg, #f97316, #fbbf24); }
.metric-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(108,99,255,0.2); }
.metric-icon  { font-size: clamp(1.5rem, 4vw, 2.2rem); margin-bottom: 6px; }
.metric-label { font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); margin-bottom: 4px; }
.metric-value { font-size: clamp(1.8rem, 5vw, 2.4rem); font-weight: 900; color: var(--text); font-family: 'Space Mono', monospace; line-height: 1; }

/* ---- QUICK TILES ---- */
.quick-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 24px;
}
@media (max-width: 600px) {
    .quick-grid { grid-template-columns: 1fr; gap: 10px; }
}
.quick-tile {
    background: linear-gradient(135deg, var(--surface), var(--surface2));
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 16px;
    transition: all 0.2s;
}
.quick-tile:hover { transform: translateY(-3px); border-color: var(--accent1); box-shadow: var(--glow); }
.quick-tile-icon  { font-size: clamp(1.4rem, 4vw, 2rem); margin-bottom: 8px; }
.quick-tile-title { font-weight: 800; font-size: clamp(0.88rem, 2.5vw, 1rem); color: var(--text); margin-bottom: 4px; }
.quick-tile-desc  { font-size: clamp(0.72rem, 2vw, 0.82rem); color: var(--muted); font-weight: 600; }

/* Quick tile info block sitting above the button */
.quick-tile-top {
    background: linear-gradient(135deg, var(--surface), var(--surface2));
    border: 1px solid var(--border);
    border-bottom: none;
    border-radius: var(--radius) var(--radius) 0 0;
    padding: 18px 16px 14px 16px;
    transition: border-color 0.2s;
}
.quick-tile-top:hover { border-color: var(--accent1); }

/* Make the button under each quick tile flush with the card above */
div[data-testid="column"] .quick-tile-top + div .stButton > button {
    border-radius: 0 0 var(--radius) var(--radius) !important;
    background: linear-gradient(90deg, rgba(108,99,255,0.18), rgba(167,139,250,0.18)) !important;
    color: var(--accent4) !important;
    box-shadow: none !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    font-size: 0.82rem !important;
    height: 2.8em !important;
    letter-spacing: 0.04em;
}
div[data-testid="column"] .quick-tile-top + div .stButton > button:hover {
    background: linear-gradient(90deg, rgba(108,99,255,0.35), rgba(167,139,250,0.3)) !important;
    color: white !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ---- SUBJECT GRID ---- */
.subject-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 10px;
    margin-bottom: 24px;
}
@media (max-width: 900px)  { .subject-grid { grid-template-columns: repeat(4, 1fr); } }
@media (max-width: 500px)  { .subject-grid { grid-template-columns: repeat(2, 1fr); gap: 8px; } }
.subject-tile {
    border-radius: 14px;
    padding: 14px 8px;
    text-align: center;
    transition: transform 0.2s;
    background: linear-gradient(135deg, #1a1d2e, #222640);
}
.subject-tile:hover { transform: translateY(-3px); }
.subject-tile-icon  { font-size: clamp(1.3rem, 3.5vw, 1.8rem); margin-bottom: 6px; }
.subject-tile-name  { font-size: clamp(0.6rem, 1.5vw, 0.78rem); font-weight: 800; color: #e2e8f0; word-break: break-word; line-height: 1.3; }
.subject-tile-count { font-size: clamp(1rem, 3vw, 1.4rem); font-weight: 900; font-family: 'Space Mono', monospace; margin-top: 4px; }
.subject-tile-label { font-size: 0.6rem; color: #64748b; font-weight: 700; }

/* ---- SECTION DIVIDER ---- */
.section-header { display: flex; align-items: center; gap: 12px; margin: 28px 0 16px 0; }
.section-header-line { flex: 1; height: 1px; background: linear-gradient(90deg, var(--border), transparent); }
.section-header-text { font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.12em; color: var(--muted); white-space: nowrap; }

/* ---- CONTENT CARD ---- */
.content-card {
    background: linear-gradient(135deg, var(--surface), var(--surface2));
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: clamp(16px, 4vw, 28px) clamp(14px, 5vw, 32px);
    margin-top: 20px;
    position: relative;
}
.content-card::before {
    content: 'AI Response';
    position: absolute;
    top: -12px; left: 20px;
    background: linear-gradient(90deg, var(--accent1), var(--accent4));
    color: white;
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    padding: 4px 12px;
    border-radius: 20px;
    text-transform: uppercase;
}

/* ---- BADGES & PILLS ---- */
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
.history-pill {
    display: inline-block;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: clamp(0.68rem, 2vw, 0.8rem);
    font-weight: 700;
    color: var(--muted);
    margin: 3px;
}

/* ---- INPUTS ---- */
.stSelectbox > div > div {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-size: 16px !important; /* prevent iOS zoom */
}
.stSelectbox > div > div:hover { border-color: var(--accent1) !important; }
.stTextArea > div > textarea {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 16px !important; /* prevent iOS zoom */
}
.stTextArea > div > textarea:focus {
    border-color: var(--accent1) !important;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.2) !important;
}

/* ---- RADIO ---- */
.stRadio > div { gap: 8px !important; flex-wrap: wrap !important; }
.stRadio label {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 700 !important;
    font-size: clamp(0.78rem, 2.2vw, 0.88rem) !important;
    min-height: 44px; /* tap target */
}
.stRadio label:hover { border-color: var(--accent1) !important; background: var(--surface2) !important; }

/* ---- BUTTONS ---- */
.stButton > button {
    background: linear-gradient(90deg, var(--accent1), var(--accent4)) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    height: 3.4em !important;
    font-size: clamp(14px, 3vw, 15px) !important;
    font-weight: 800 !important;
    font-family: 'Nunito', sans-serif !important;
    letter-spacing: 0.04em;
    transition: all 0.25s !important;
    box-shadow: 0 4px 15px rgba(108,99,255,0.35) !important;
    width: 100%;
    min-height: 44px; /* tap target */
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
.stSelectbox label, .stTextArea label {
    color: var(--muted) !important;
    font-weight: 700 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ---- SUBJECT BANNER ---- */
.subject-banner {
    background: linear-gradient(135deg, #1a1d2e, #222640);
    border-radius: 14px;
    padding: clamp(14px, 3vw, 20px) clamp(14px, 4vw, 24px);
    margin: 16px 0;
    display: flex;
    gap: 16px;
    align-items: center;
    flex-wrap: wrap;
}

/* ---- PROMPT CHIPS ---- */
.prompt-chips { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 18px; }
.prompt-chip {
    background: #1a1d2e;
    border: 1px solid rgba(108,99,255,0.2);
    border-radius: 20px;
    padding: 8px 14px;
    font-size: clamp(0.72rem, 2vw, 0.8rem);
    font-weight: 700;
    color: #94a3b8;
    min-height: 36px;
    display: flex;
    align-items: center;
}

/* ---- MOBILE: stack columns, bigger taps, bottom nav ---- */
@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    .stRadio > div {
        flex-direction: column !important;
    }
    .stRadio label {
        width: 100% !important;
    }
    .main .block-container {
        padding-bottom: 90px !important;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }
}

/* ---- MOBILE BOTTOM NAV ---- */
.mobile-nav {
    display: none;
}
@media (max-width: 768px) {
    .mobile-nav {
        display: flex;
        position: fixed;
        bottom: 0; left: 0; right: 0;
        background: rgba(18, 21, 43, 0.97);
        border-top: 1px solid rgba(108,99,255,0.3);
        z-index: 9999;
        padding: 8px 0 max(10px, env(safe-area-inset-bottom));
        justify-content: space-around;
        align-items: center;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 -4px 24px rgba(0,0,0,0.5);
    }
    .mobile-nav a {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 3px;
        text-decoration: none;
        color: #4a5568;
        font-size: 0.6rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 6px 14px;
        border-radius: 12px;
        transition: color 0.2s, background 0.2s;
        min-width: 60px;
        min-height: 50px;
        justify-content: center;
    }
    .mobile-nav a.active {
        color: #a78bfa;
        background: rgba(108,99,255,0.15);
    }
    .mobile-nav a .nav-icon {
        font-size: 1.5rem;
        line-height: 1;
    }
}

/* ---- SCROLLBAR ---- */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent1); }
</style>
""", unsafe_allow_html=True)

# ======================================================
# DATA
# ======================================================
SUBJECTS = ["Mathematics", "Science", "Social Science", "English", "Hindi",
            "Artificial Intelligence", "Information Technology"]

CHAPTERS = {
    "Mathematics": [
        "Real Numbers", "Polynomials", "Pair of Linear Equations in Two Variables",
        "Quadratic Equations", "Arithmetic Progressions", "Triangles",
        "Coordinate Geometry", "Introduction to Trigonometry",
        "Some Applications of Trigonometry", "Circles",
        "Areas Related to Circles", "Surface Areas and Volumes",
        "Statistics", "Probability"
    ],
    "Science": [
        "Chemical Reactions and Equations", "Acids, Bases and Salts",
        "Metals and Non-metals", "Carbon and its Compounds",
        "Life Processes", "Control and Coordination",
        "How do Organisms Reproduce?", "Heredity",
        "Light – Reflection and Refraction", "The Human Eye and the Colourful World",
        "Electricity", "Magnetic Effects of Electric Current", "Our Environment"
    ],
    "Social Science": [
        "The Rise of Nationalism in Europe", "Nationalism in India",
        "The Making of a Global World", "The Age of Industrialisation",
        "Print Culture and the Modern World", "Resources and Development",
        "Forest and Wildlife Resources", "Water Resources", "Agriculture",
        "Minerals and Energy Resources", "Manufacturing Industries",
        "Lifelines of National Economy", "Power Sharing", "Federalism",
        "Gender, Religion and Caste", "Political Parties",
        "Outcomes of Democracy", "Development",
        "Sectors of the Indian Economy", "Money and Credit",
        "Globalisation and the Indian Economy", "Consumer Rights"
    ],
    "English": [
        "A Letter to God", "Nelson Mandela: Long Walk to Freedom",
        "Two Stories about Flying", "From the Diary of Anne Frank",
        "Glimpses of India", "Mijbil the Otter", "Madam Rides the Bus",
        "The Sermon at Benares", "The Proposal", "A Triumph of Surgery",
        "The Thief's Story", "The Midnight Visitor", "A Question of Trust",
        "Footprints without Feet", "The Making of a Scientist",
        "The Necklace", "Bholi", "The Book That Saved the Earth"
    ],
    "Hindi": [
        "सूरदास — पद", "तुलसीदास — राम-लक्ष्मण-परशुराम संवाद",
        "देव — सवैया और कवित्त", "जयशंकर प्रसाद — आत्मकथ्य",
        "सूर्यकांत त्रिपाठी 'निराला' — उत्साह और अट नहीं रही",
        "नागार्जुन — यह दंतुरहित मुस्कान और फसल",
        "गिरिजाकुमार माथुर — छाया मत छूना", "ऋतुराज — कन्यादान",
        "मंगलेश डबराल — संगतकार", "स्वयं प्रकाश — नेताजी का चश्मा",
        "रामवृक्ष बेनीपुरी — बालगोबिन भगत", "यशपाल — लखनवी अंदाज़",
        "सर्वेश्वर दयाल सक्सेना — मानवीय करुणा की दिव्य चमक",
        "मन्नू भंडारी — एक कहानी यह भी",
        "महावीर प्रसाद द्विवेदी — स्त्री शिक्षा के विरोधी कुतर्कों का खंडन",
        "यतींद्र मिश्र — नौबतखाने में इबादत",
        "भदंत आनंद कौसल्यायन — संस्कृति"
    ],
    "Artificial Intelligence": [
        "Introduction to Artificial Intelligence", "AI Project Cycle",
        "Problem Scoping", "Data Acquisition", "Data Exploration",
        "Modelling", "Evaluation", "Natural Language Processing (NLP)",
        "Computer Vision", "Machine Learning Basics",
        "Neural Networks and Deep Learning", "AI Ethics and Bias",
        "AI Applications in Society", "Future of AI and Emerging Trends"
    ],
    "Information Technology": [
        "Communication Skills", "Self-Management Skills", "ICT Skills",
        "Entrepreneurial Skills", "Green Skills",
        "Digital Documentation (Advanced) — LibreOffice Writer",
        "Electronic Spreadsheet (Advanced) — LibreOffice Calc",
        "Database Management System — LibreOffice Base",
        "Web Applications and Security", "HTML Basics and Structure",
        "Working with Tables and Forms in HTML", "Introduction to CSS",
        "Cyber Safety and Ethics", "E-Commerce and Digital Payments"
    ]
}

SUBJECT_COLORS = {
    "Mathematics":           "#6c63ff",
    "Science":               "#22d3ee",
    "Social Science":        "#4ade80",
    "English":               "#f97316",
    "Hindi":                 "#f472b6",
    "Artificial Intelligence": "#facc15",
    "Information Technology":  "#818cf8",
}

SUBJECT_ICONS = {
    "Mathematics":           "📐",
    "Science":               "🔬",
    "Social Science":        "🌍",
    "English":               "📖",
    "Hindi":                 "✍️",
    "Artificial Intelligence": "🤖",
    "Information Technology":  "💻",
}

# ======================================================
# SIDEBAR (desktop / tablet)
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
        st.session_state.exam_mode_default = "Full Question Paper (80 marks)"
    if st.button("🎯  Chapter-Wise Test"):
        st.session_state.page = "Papers"
        st.session_state.exam_mode_default = "Chapter-Wise Practice Test"
    if st.button("🔘  MCQ Quiz"):
        st.session_state.page = "Papers"
        st.session_state.exam_mode_default = "MCQ Quiz (Auto-Evaluated)"
    if st.button("📅  Previous Year Papers"):
        st.session_state.page = "PYQ"
    if st.button("💬  Doubt Solver"):
        st.session_state.page = "Doubt"
    st.markdown("---")
    level = st.session_state.xp // 100 + 1
    xp_in_level = st.session_state.xp % 100
    st.markdown(f"""
<div style='padding:14px;background:rgba(108,99,255,0.1);border-radius:12px;border:1px solid rgba(108,99,255,0.2);'>
  <div style='font-size:0.7rem;font-weight:800;letter-spacing:0.08em;color:#94a3b8;text-transform:uppercase;margin-bottom:6px;'>Level {level} Scholar</div>
  <div style='font-size:1.4rem;font-weight:900;color:#e2e8f0;font-family:Space Mono,monospace;'>⭐ {st.session_state.xp} XP</div>
  <div style='margin-top:10px;background:rgba(255,255,255,0.08);border-radius:20px;height:6px;overflow:hidden;'>
    <div style='height:100%;width:{xp_in_level}%;background:linear-gradient(90deg,#6c63ff,#a78bfa);border-radius:20px;'></div>
  </div>
  <div style='font-size:0.68rem;color:#94a3b8;margin-top:4px;font-weight:600;'>{xp_in_level}/100 to next level</div>
</div>
<div class='sidebar-watermark'>CBSE Grade 10 · 2024-25</div>
    """, unsafe_allow_html=True)

# ======================================================
# MOBILE BOTTOM NAV BAR
# ======================================================
_cur_page = st.session_state.page
_pages = [("Dashboard","🏠","Home"), ("Study","📚","Study"), ("Papers","📜","Exam"), ("PYQ","📅","PYQs"), ("ChapTest","🎯","Ch.Test"), ("Doubt","💬","Doubt")]
_links = "".join([
    f"<a class='{'active' if _cur_page==p else ''}' href='?nav={p}' target='_self'>"
    f"<span class='nav-icon'>{ico}</span>{lbl}</a>"
    for p, ico, lbl in _pages
])
st.markdown(f"<nav class='mobile-nav'>{_links}</nav>", unsafe_allow_html=True)


# ======================================================
# DASHBOARD
# ======================================================
if st.session_state.page == "Dashboard":

    st.markdown("<div class='page-header'>📘 CBSE Smart Tutor</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Your AI-powered study companion for Grade 10</div>", unsafe_allow_html=True)

    level = st.session_state.xp // 100 + 1
    st.markdown(f"""
<div class='metrics-grid'>
  <div class='metric-card xp'>
    <div class='metric-icon'>⭐</div>
    <div class='metric-label'>Total XP Earned</div>
    <div class='metric-value'>{st.session_state.xp}</div>
  </div>
  <div class='metric-card topics'>
    <div class='metric-icon'>📖</div>
    <div class='metric-label'>Topics Studied</div>
    <div class='metric-value'>{len(st.session_state.topic_history)}</div>
  </div>
  <div class='metric-card streak'>
    <div class='metric-icon'>🏆</div>
    <div class='metric-label'>Scholar Level</div>
    <div class='metric-value'>{level}</div>
  </div>
</div>
    """, unsafe_allow_html=True)

    st.markdown("""
<div class='section-header'>
  <div class='section-header-text'>Quick Access</div>
  <div class='section-header-line'></div>
</div>
    """, unsafe_allow_html=True)

    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        st.markdown("""
<div class='quick-tile-top'>
  <div class='quick-tile-icon'>📚</div>
  <div class='quick-tile-title'>Study Mode</div>
  <div class='quick-tile-desc'>NCERT-based concept explanations and PYQs</div>
</div>""", unsafe_allow_html=True)
        if st.button("Go to Study Mode", key="qa_study"):
            st.session_state.page = "Study"
            st.rerun()

    with qa2:
        st.markdown("""
<div class='quick-tile-top'>
  <div class='quick-tile-icon'>📜</div>
  <div class='quick-tile-title'>Exam Simulation</div>
  <div class='quick-tile-desc'>Full-length CBSE-style question papers</div>
</div>""", unsafe_allow_html=True)
        if st.button("Go to Exam Simulation", key="qa_exam"):
            st.session_state.page = "Papers"
            st.rerun()

    with qa3:
        st.markdown("""
<div class='quick-tile-top'>
  <div class='quick-tile-icon'>💬</div>
  <div class='quick-tile-title'>Doubt Solver</div>
  <div class='quick-tile-desc'>Get instant answers from your AI teacher</div>
</div>""", unsafe_allow_html=True)
        if st.button("Go to Doubt Solver", key="qa_doubt"):
            st.session_state.page = "Doubt"
            st.rerun()

    st.markdown("""
<div class='section-header'>
  <div class='section-header-text'>More Tools</div>
  <div class='section-header-line'></div>
</div>
    """, unsafe_allow_html=True)
    qa4, qa5 = st.columns(2)
    with qa4:
        st.markdown("""
<div class='quick-tile-top'>
  <div class='quick-tile-icon'>📅</div>
  <div class='quick-tile-title'>Previous Year Papers</div>
  <div class='quick-tile-desc'>CBSE board papers from 2019–2023 for all subjects</div>
</div>""", unsafe_allow_html=True)
        if st.button("Go to Previous Year Papers", key="qa_pyq"):
            st.session_state.page = "PYQ"
            st.rerun()
    with qa5:
        st.markdown("""
<div class='quick-tile-top'>
  <div class='quick-tile-icon'>🎯</div>
  <div class='quick-tile-title'>Chapter-Wise Test</div>
  <div class='quick-tile-desc'>Practice one chapter at a time with custom marks</div>
</div>""", unsafe_allow_html=True)
        if st.button("Go to Chapter Test", key="qa_chap"):
            st.session_state.page = "Papers"
            st.rerun()

    st.markdown("""
<div class='section-header'>
  <div class='section-header-text'>Subjects</div>
  <div class='section-header-line'></div>
</div>
    """, unsafe_allow_html=True)

    tiles_html = "<div class='subject-grid'>"
    for subject in SUBJECTS:
        count = sum(1 for s, _ in st.session_state.topic_history if s == subject)
        color = SUBJECT_COLORS[subject]
        icon = SUBJECT_ICONS[subject]
        tiles_html += (
            f"<div class='subject-tile' style='border:1px solid {color}30;border-top:3px solid {color};'>"
            f"<div class='subject-tile-icon'>{icon}</div>"
            f"<div class='subject-tile-name'>{subject}</div>"
            f"<div class='subject-tile-count' style='color:{color};'>{count}</div>"
            f"<div class='subject-tile-label'>sessions</div>"
            f"</div>"
        )
    tiles_html += "</div>"
    st.markdown(tiles_html, unsafe_allow_html=True)

    if st.session_state.topic_history:
        st.markdown("""
<div class='section-header'>
  <div class='section-header-text'>Recent Activity</div>
  <div class='section-header-line'></div>
</div>
        """, unsafe_allow_html=True)
        pills = "".join([
            f"<span class='history-pill'>{SUBJECT_ICONS.get(s,'📘')} {s} · {ch}</span>"
            for s, ch in reversed(st.session_state.topic_history[-10:])
        ])
        st.markdown(f"<div style='line-height:2.8;'>{pills}</div>", unsafe_allow_html=True)


# ======================================================
# STUDY MODE
# ======================================================
elif st.session_state.page == "Study":

    st.markdown("<div class='page-header'>📚 Study Mode</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>NCERT-aligned lessons crafted just for you</div>", unsafe_allow_html=True)

    # Single column layout — works on all screen sizes
    subject = st.selectbox("🎯 Subject", SUBJECTS)
    chapter = st.selectbox("📌 Chapter", CHAPTERS.get(subject, []))

    st.markdown("<br>", unsafe_allow_html=True)
    mode = st.radio("📋 Learning Mode", [
        "Concept Clarity",
        "Exam-Oriented Answers",
        "Previous Year Questions"
    ])
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
<div style='display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:24px 0 8px 0;'>
  <span style='font-size:1.3rem;'>{icon}</span>
  <span style='font-weight:800;color:#e2e8f0;font-size:clamp(0.85rem,2.5vw,1rem);'>{subject} · {chapter}</span>
  <span style='background:linear-gradient(90deg,{color},{color}88);color:white;font-size:0.68rem;
               font-weight:800;padding:3px 12px;border-radius:20px;text-transform:uppercase;letter-spacing:0.06em;'>{mode}</span>
  <span class='xp-badge' style='margin-left:auto;'>+20 XP</span>
</div>
        """, unsafe_allow_html=True)
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.write(st.session_state.generated_content)
        st.markdown("</div>", unsafe_allow_html=True)


# ======================================================
# EXAM SIMULATION  (full paper OR chapter-wise OR MCQ quiz)
# ======================================================
elif st.session_state.page == "Papers":

    st.markdown("<div class='page-header'>📜 Exam Simulation</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Full papers, chapter practice, or interactive MCQ quiz</div>", unsafe_allow_html=True)

    subject = st.selectbox("🎯 Choose Subject", SUBJECTS)
    color   = SUBJECT_COLORS.get(subject, "#6c63ff")
    icon    = SUBJECT_ICONS.get(subject, "📘")

    sim_mode = st.radio("📋 Simulation Type", [
        "Full Question Paper (80 marks)",
        "Chapter-Wise Practice Test",
        "MCQ Quiz (Auto-Evaluated)"
    ], index=["Full Question Paper (80 marks)", "Chapter-Wise Practice Test", "MCQ Quiz (Auto-Evaluated)"].index(
        st.session_state.exam_mode_default
    ) if st.session_state.exam_mode_default in [
        "Full Question Paper (80 marks)", "Chapter-Wise Practice Test", "MCQ Quiz (Auto-Evaluated)"
    ] else 0)
    st.session_state.exam_mode_default = sim_mode

    # ── FULL PAPER ──────────────────────────────────────
    if sim_mode == "Full Question Paper (80 marks)":
        info_line = "Full syllabus · 80 marks · CBSE pattern"
        st.markdown(f"""
<div class='subject-banner' style='border:1px solid {color}40;'>
  <span style='font-size:clamp(1.8rem,5vw,2.5rem);'>{icon}</span>
  <div>
    <div style='font-weight:800;font-size:clamp(0.95rem,3vw,1.1rem);color:#e2e8f0;'>{subject} — Class 10</div>
    <div style='font-size:clamp(0.72rem,2vw,0.82rem);color:#94a3b8;font-weight:600;margin-top:2px;'>{info_line}</div>
  </div>
</div>""", unsafe_allow_html=True)

        if st.button("🚀 Generate Full Question Paper"):
            with st.spinner("📝 Setting your paper..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an official CBSE paper setter. Format papers clearly with sections, marks, and instructions exactly as CBSE does."},
                        {"role": "user",   "content": (
                            f"Generate a complete, realistic CBSE Class 10 question paper for {subject}. "
                            f"Total 80 marks. Include Section A (MCQs/1-mark), Section B (2-mark), "
                            f"Section C (3-mark), Section D (5-mark) and Section E (case-based). "
                            f"Follow latest CBSE pattern with all general instructions."
                        )}
                    ], temperature=0.4
                )
                st.session_state.xp += 10
            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
            st.write(response.choices[0].message.content)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<span class='xp-badge'>+10 XP Earned!</span>", unsafe_allow_html=True)

    # ── CHAPTER-WISE PRACTICE TEST ───────────────────────
    elif sim_mode == "Chapter-Wise Practice Test":
        chapter = st.selectbox("📌 Choose Chapter", CHAPTERS.get(subject, []))
        marks   = st.select_slider("📊 Marks for this test", options=[10, 20, 25, 30, 40, 50], value=25)
        info_line = f"{chapter} · {marks} marks"
        st.markdown(f"""
<div class='subject-banner' style='border:1px solid {color}40;'>
  <span style='font-size:clamp(1.8rem,5vw,2.5rem);'>{icon}</span>
  <div>
    <div style='font-weight:800;font-size:clamp(0.95rem,3vw,1.1rem);color:#e2e8f0;'>{subject} — Class 10</div>
    <div style='font-size:clamp(0.72rem,2vw,0.82rem);color:#94a3b8;font-weight:600;margin-top:2px;'>{info_line}</div>
  </div>
</div>""", unsafe_allow_html=True)

        if st.button(f"🚀 Generate {marks}-Mark Chapter Test"):
            with st.spinner("📝 Setting your chapter test..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an official CBSE paper setter. Format papers clearly with sections, marks, and instructions exactly as CBSE does."},
                        {"role": "user",   "content": (
                            f"Generate a {marks}-mark CBSE Class 10 chapter-wise practice test for "
                            f"Subject: {subject}, Chapter: {chapter}. "
                            f"Include a mix of 1-mark, 2-mark, 3-mark and 5-mark questions as appropriate. "
                            f"Follow official CBSE question paper format with instructions."
                        )}
                    ], temperature=0.4
                )
                st.session_state.xp += 5
            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
            st.write(response.choices[0].message.content)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<span class='xp-badge'>+5 XP Earned!</span>", unsafe_allow_html=True)

    # ── MCQ QUIZ (AUTO-EVALUATED) ────────────────────────
    elif sim_mode == "MCQ Quiz (Auto-Evaluated)":
        chapter  = st.selectbox("📌 Choose Chapter", CHAPTERS.get(subject, []))
        n_mcqs   = st.select_slider("🔢 Number of Questions", options=[5, 10, 15, 20], value=10)
        info_line = f"{chapter} · {n_mcqs} MCQs · Auto-evaluated"

        st.markdown(f"""
<div class='subject-banner' style='border:1px solid {color}40;'>
  <span style='font-size:clamp(1.8rem,5vw,2.5rem);'>{icon}</span>
  <div>
    <div style='font-weight:800;font-size:clamp(0.95rem,3vw,1.1rem);color:#e2e8f0;'>{subject} — Class 10</div>
    <div style='font-size:clamp(0.72rem,2vw,0.82rem);color:#94a3b8;font-weight:600;margin-top:2px;'>{info_line}</div>
  </div>
</div>""", unsafe_allow_html=True)

        # Reset quiz if subject/chapter changed
        if (st.session_state.mcq_subject != subject or
                st.session_state.mcq_chapter != chapter):
            st.session_state.mcq_questions = None
            st.session_state.mcq_answers   = {}
            st.session_state.mcq_submitted = False

        # ── Generate MCQs ──
        if st.session_state.mcq_questions is None:
            if st.button("🎲 Generate MCQ Quiz"):
                with st.spinner("🧠 Preparing your quiz..."):
                    mcq_prompt = f"""Generate exactly {n_mcqs} multiple choice questions for CBSE Class 10 {subject}, Chapter: {chapter}.

Return ONLY a Python list of dicts in this exact format, nothing else before or after:
[
  {{
    "q": "Question text here?",
    "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
    "answer": "A",
    "explanation": "Brief explanation of why A is correct."
  }},
  ...
]
Each question must have exactly 4 options labelled A, B, C, D. The answer field must be just the letter A, B, C or D."""

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a CBSE MCQ generator. Return only valid Python list syntax, no markdown, no backticks, no extra text."},
                            {"role": "user",   "content": mcq_prompt}
                        ],
                        temperature=0.3
                    )
                    raw = response.choices[0].message.content.strip()
                    # Strip any accidental markdown fences
                    raw = raw.replace("```python", "").replace("```", "").strip()
                    try:
                        import ast as _ast
                        questions = _ast.literal_eval(raw)
                        st.session_state.mcq_questions = questions
                        st.session_state.mcq_answers   = {}
                        st.session_state.mcq_submitted = False
                        st.session_state.mcq_subject   = subject
                        st.session_state.mcq_chapter   = chapter
                    except Exception as e:
                        st.error(f"Could not parse quiz questions. Please try again. ({e})")
                st.rerun()

        # ── Render Quiz ──
        elif not st.session_state.mcq_submitted:
            questions = st.session_state.mcq_questions
            st.markdown(f"""
<div class='section-header'>
  <div class='section-header-text'>Answer all {len(questions)} questions</div>
  <div class='section-header-line'></div>
</div>""", unsafe_allow_html=True)

            with st.form("mcq_form"):
                user_answers = {}
                for i, q in enumerate(questions):
                    st.markdown(f"""
<div style='background:linear-gradient(135deg,#1a1d2e,#222640);border:1px solid rgba(108,99,255,0.15);
            border-left:3px solid {color};border-radius:12px;padding:16px 18px;margin-bottom:12px;'>
  <div style='font-weight:800;font-size:clamp(0.88rem,2.5vw,0.95rem);color:#e2e8f0;margin-bottom:10px;'>
    Q{i+1}. {q["q"]}
  </div>
</div>""", unsafe_allow_html=True)
                    user_answers[i] = st.radio(
                        f"q_{i+1}",
                        options=q["options"],
                        key=f"mcq_{i}",
                        label_visibility="collapsed"
                    )

                submitted = st.form_submit_button("✅ Submit & Evaluate", use_container_width=True)
                if submitted:
                    # Extract just the letter from selected option e.g. "A. option" → "A"
                    st.session_state.mcq_answers = {
                        i: (ans.split(".")[0].strip() if ans else None)
                        for i, ans in user_answers.items()
                    }
                    st.session_state.mcq_submitted = True
                    st.rerun()

        # ── Show Results ──
        else:
            questions  = st.session_state.mcq_questions
            answers    = st.session_state.mcq_answers
            total      = len(questions)
            correct    = sum(1 for i, q in enumerate(questions) if answers.get(i) == q["answer"])
            wrong      = sum(1 for i, q in enumerate(questions) if answers.get(i) != q["answer"] and answers.get(i) is not None)
            pct        = round((correct / total) * 100)
            xp_earned  = correct * 2

            if pct >= 80:
                grade, grade_color, grade_emoji = "Excellent!", "#4ade80", "🏆"
            elif pct >= 60:
                grade, grade_color, grade_emoji = "Good Job!", "#facc15", "⭐"
            elif pct >= 40:
                grade, grade_color, grade_emoji = "Keep Practising", "#f97316", "💪"
            else:
                grade, grade_color, grade_emoji = "Need More Revision", "#f87171", "📖"

            st.session_state.xp += xp_earned

            # Score card
            st.markdown(f"""
<div style='background:linear-gradient(135deg,#1a1d2e,#222640);border:1px solid {grade_color}40;
            border-radius:16px;padding:28px 24px;text-align:center;margin:20px 0;position:relative;overflow:hidden;'>
  <div style='position:absolute;top:0;left:0;right:0;height:4px;
              background:linear-gradient(90deg,{color},{grade_color});'></div>
  <div style='font-size:3rem;margin-bottom:8px;'>{grade_emoji}</div>
  <div style='font-size:clamp(1.8rem,6vw,2.8rem);font-weight:900;color:{grade_color};
              font-family:Space Mono,monospace;line-height:1;'>{correct}/{total}</div>
  <div style='font-size:clamp(1rem,3vw,1.3rem);font-weight:800;color:#e2e8f0;margin:6px 0 4px;'>{grade}</div>
  <div style='font-size:0.82rem;color:#94a3b8;font-weight:600;'>{pct}% score · {correct} correct · {wrong} wrong</div>
  <div style='margin-top:14px;'><span class='xp-badge'>+{xp_earned} XP Earned!</span></div>
</div>

<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:20px;'>
  <div style='background:#1a1d2e;border:1px solid #4ade8040;border-radius:12px;padding:14px;text-align:center;'>
    <div style='font-size:1.6rem;font-weight:900;color:#4ade80;font-family:Space Mono,monospace;'>{correct}</div>
    <div style='font-size:0.7rem;font-weight:800;color:#94a3b8;text-transform:uppercase;letter-spacing:0.08em;'>Correct</div>
  </div>
  <div style='background:#1a1d2e;border:1px solid #f8717140;border-radius:12px;padding:14px;text-align:center;'>
    <div style='font-size:1.6rem;font-weight:900;color:#f87171;font-family:Space Mono,monospace;'>{wrong}</div>
    <div style='font-size:0.7rem;font-weight:800;color:#94a3b8;text-transform:uppercase;letter-spacing:0.08em;'>Wrong</div>
  </div>
  <div style='background:#1a1d2e;border:1px solid {color}40;border-radius:12px;padding:14px;text-align:center;'>
    <div style='font-size:1.6rem;font-weight:900;color:{color};font-family:Space Mono,monospace;'>{pct}%</div>
    <div style='font-size:0.7rem;font-weight:800;color:#94a3b8;text-transform:uppercase;letter-spacing:0.08em;'>Score</div>
  </div>
</div>
""", unsafe_allow_html=True)

            # Answer review
            st.markdown("""
<div class='section-header'>
  <div class='section-header-text'>Answer Review</div>
  <div class='section-header-line'></div>
</div>""", unsafe_allow_html=True)

            for i, q in enumerate(questions):
                user_ans    = answers.get(i)
                correct_ans = q["answer"]
                is_correct  = user_ans == correct_ans
                border_col  = "#4ade80" if is_correct else "#f87171"
                icon_result = "✅" if is_correct else "❌"
                bg_col      = "rgba(74,222,128,0.06)" if is_correct else "rgba(248,113,113,0.06)"

                options_html = ""
                for opt in q["options"]:
                    opt_letter = opt.split(".")[0].strip()
                    if opt_letter == correct_ans:
                        opt_style = f"color:#4ade80;font-weight:800;"
                        opt_badge = " ✓"
                    elif opt_letter == user_ans and not is_correct:
                        opt_style = f"color:#f87171;font-weight:800;text-decoration:line-through;"
                        opt_badge = " ✗"
                    else:
                        opt_style = "color:#94a3b8;"
                        opt_badge = ""
                    options_html += f"<div style='{opt_style}font-size:0.85rem;padding:2px 0;'>{opt}{opt_badge}</div>"

                st.markdown(f"""
<div style='background:{bg_col};border:1px solid {border_col}30;border-left:3px solid {border_col};
            border-radius:12px;padding:16px 18px;margin-bottom:10px;'>
  <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:10px;flex-wrap:wrap;'>
    <div style='font-weight:800;font-size:clamp(0.85rem,2.5vw,0.92rem);color:#e2e8f0;flex:1;'>
      {icon_result} Q{i+1}. {q["q"]}
    </div>
  </div>
  <div style='margin:10px 0 8px 0;'>{options_html}</div>
  <div style='background:rgba(108,99,255,0.1);border-radius:8px;padding:8px 12px;
              font-size:0.8rem;color:#a78bfa;font-weight:700;'>
    💡 {q["explanation"]}
  </div>
</div>""", unsafe_allow_html=True)

            st.session_state.topic_history.append((subject, f"MCQ: {chapter}"))
            if st.button("🔄 Try Again with New Questions"):
                st.session_state.mcq_questions = None
                st.session_state.mcq_answers   = {}
                st.session_state.mcq_submitted = False
                st.rerun()


# ======================================================
# PREVIOUS YEAR PAPERS
# ======================================================
elif st.session_state.page == "PYQ":

    st.markdown("<div class='page-header'>📅 Previous Year Papers</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>CBSE Board exam questions from 2019 to 2023, reconstructed by AI</div>", unsafe_allow_html=True)

    subject = st.selectbox("🎯 Choose Subject", SUBJECTS)
    color   = SUBJECT_COLORS.get(subject, "#6c63ff")
    icon    = SUBJECT_ICONS.get(subject, "📘")

    year = st.select_slider(
        "📆 Select Year",
        options=[2019, 2020, 2021, 2022, 2023],
        value=2023
    )

    pyq_type = st.radio("📋 Paper Type", [
        "Full Board Paper",
        "Important Questions Only (Top 30)",
        "Chapter-Wise PYQs"
    ])

    if pyq_type == "Chapter-Wise PYQs":
        chapter = st.selectbox("📌 Choose Chapter", CHAPTERS.get(subject, []))
        prompt_text = (
            f"Reconstruct previous year CBSE Class 10 board exam questions for "
            f"Subject: {subject}, Chapter: {chapter}, Year: {year}. "
            f"List all questions that appeared from this chapter in the {year} CBSE board exam. "
            f"Include the marks weightage for each question. "
            f"If exact questions aren't available, generate highly likely questions based on the {year} CBSE pattern and syllabus for this chapter."
        )
        info_line = f"{chapter} · {year} Board Exam"
    elif pyq_type == "Important Questions Only (Top 30)":
        chapter = None
        prompt_text = (
            f"List the top 30 most important previous year CBSE Class 10 board exam questions "
            f"for {subject} from the {year} board exam. "
            f"Group them by chapter. Include marks for each. "
            f"Focus on questions most likely to repeat in upcoming exams."
        )
        info_line = f"Top 30 important questions · {year}"
    else:
        chapter = None
        prompt_text = (
            f"Reconstruct the complete CBSE Class 10 {subject} board question paper from {year}. "
            f"Include all sections (A, B, C, D, E), all questions with marks, "
            f"general instructions, and time duration exactly as it appeared in the {year} CBSE board exam. "
            f"Note at the top that this is an AI reconstruction for practice purposes."
        )
        info_line = f"Full Board Paper · {year} · 80 marks"

    # Year badges
    year_html = "<div style='display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 4px 0;'>"
    for y in [2019, 2020, 2021, 2022, 2023]:
        active_style = f"background:linear-gradient(90deg,{color},{color}99);color:white;border-color:{color};" if y == year else "background:#1a1d2e;color:#94a3b8;border-color:rgba(108,99,255,0.2);"
        year_html += f"<span style='{active_style}border:1px solid;border-radius:20px;padding:4px 14px;font-size:0.78rem;font-weight:800;'>{y}</span>"
    year_html += "</div>"

    st.markdown(f"""
<div class='subject-banner' style='border:1px solid {color}40;'>
  <span style='font-size:clamp(1.8rem,5vw,2.5rem);'>{icon}</span>
  <div style='flex:1;'>
    <div style='font-weight:800;font-size:clamp(0.95rem,3vw,1.1rem);color:#e2e8f0;'>{subject} — Class 10</div>
    <div style='font-size:clamp(0.72rem,2vw,0.82rem);color:#94a3b8;font-weight:600;margin-top:2px;'>{info_line}</div>
    {year_html}
  </div>
</div>
    """, unsafe_allow_html=True)

    if st.button(f"📄 Load {year} Paper"):
        with st.spinner(f"📚 Retrieving {year} questions for {subject}..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": (
                        "You are a CBSE exam expert with deep knowledge of all previous year board papers. "
                        "Reconstruct papers as accurately as possible. Always note at the top that this is "
                        "an AI-reconstructed paper for practice. Format clearly with sections and marks."
                    )},
                    {"role": "user", "content": prompt_text}
                ],
                temperature=0.2
            )
            st.session_state.xp += 5
            st.session_state.topic_history.append((subject, f"PYQ {year}"))

        st.markdown(f"""
<div style='background:linear-gradient(135deg,#1a1d2e,#222640);border:1px solid {color}30;
            border-radius:14px;padding:14px 18px;margin:16px 0;
            display:flex;align-items:center;gap:14px;flex-wrap:wrap;'>
  <span style='font-size:1.8rem;'>{icon}</span>
  <div>
    <div style='font-weight:800;color:#e2e8f0;font-size:0.95rem;'>{subject} · {year} Board Paper</div>
    <div style='font-size:0.75rem;color:#94a3b8;font-weight:600;margin-top:2px;'>AI-reconstructed for practice · CBSE pattern</div>
  </div>
  <span class='xp-badge' style='margin-left:auto;'>+5 XP</span>
</div>
        """, unsafe_allow_html=True)
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.write(response.choices[0].message.content)
        st.markdown("</div>", unsafe_allow_html=True)


# ======================================================
# DOUBT SOLVER
# ======================================================
elif st.session_state.page == "Doubt":

    st.markdown("<div class='page-header'>💬 Doubt Solver</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Your AI teacher is ready — ask anything!</div>", unsafe_allow_html=True)

    st.markdown("""
<div class='prompt-chips'>
  <span class='prompt-chip'>💡 Explain photosynthesis</span>
  <span class='prompt-chip'>💡 What is HCF?</span>
  <span class='prompt-chip'>💡 Causes of WW1</span>
  <span class='prompt-chip'>💡 What is machine learning?</span>
  <span class='prompt-chip'>💡 Difference between HTML and CSS</span>
</div>
    """, unsafe_allow_html=True)

    question = st.text_area("🤔 Your Question", placeholder="Type your doubt here... I'll explain it simply!", height=130)

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

        q_preview = question[:200] + ("..." if len(question) > 200 else "")
        st.markdown(f"""
<div style='background:linear-gradient(135deg,#1a1d2e,#222640);border:1px solid rgba(34,211,238,0.2);
            border-radius:14px;padding:clamp(12px,3vw,16px) clamp(14px,4vw,20px);margin:16px 0;
            display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap;'>
  <span style='font-size:1.2rem;'>❓</span>
  <div style='font-weight:700;color:#94a3b8;font-size:clamp(0.82rem,2.5vw,0.9rem);flex:1;min-width:150px;'>
    {q_preview}
  </div>
</div>
        """, unsafe_allow_html=True)
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.write(response.choices[0].message.content)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<span class='xp-badge'>+5 XP Earned!</span>", unsafe_allow_html=True)
