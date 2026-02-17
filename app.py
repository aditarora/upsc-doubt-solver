import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# ── Load secrets ─────────────────────────────────────────────────────────────
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 GEMINI_API_KEY missing! Add it to `.env` or Hugging Face Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# Current stable model recommendation (2026)
MODEL_NAME = "gemini-2.5-flash"           # or "gemini-flash-latest", "gemini-3-flash"

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config={"temperature": 0.7, "max_output_tokens": 2048}
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UPSC Insight – AI Doubt Solver",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Professional Dark Theme CSS ──────────────────────────────────────────────
st.markdown("""
    <style>
    /* Main background & text */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }

    /* Headers & titles */
    h1, h2, h3, h4, h5, h6 {
        color: #58a6ff !important;
    }

    /* Chat container improvements */
    .stChatMessage {
        background: transparent !important;
        padding: 0 !important;
    }

    /* Custom chat bubbles */
    .chat-user {
        background-color: #238636;
        color: white;
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 12px 8px auto;
        max-width: 80%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }

    .chat-ai {
        background-color: #161b22;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px auto 8px 12px;
        max-width: 80%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }

    /* Input box */
    .stChatInput > div > div > textarea {
        background-color: #0d1117 !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
    }

    .stChatInput button {
        background-color: #238636 !important;
        color: white !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }

    .sidebar .sidebar-content {
        background-color: #161b22;
    }

    /* Buttons in sidebar */
    .stButton > button {
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
    }

    .stButton > button:hover {
        background-color: #30363d;
        border-color: #58a6ff;
    }

    /* Spinner & status */
    .stSpinner > div > div {
        border-top-color: #58a6ff !important;
    }

    /* Footer */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #010409;
        color: #8b949e;
        text-align: center;
        padding: 10px;
        font-size: 0.85rem;
        border-top: 1px solid #30363d;
        z-index: 999;
    }

    /* Hide default footer */
    footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<h1 style="text-align: center; margin-bottom: 0.4rem;">UPSC Insight</h1>',
    unsafe_allow_html=True
)
st.markdown(
    '<p style="text-align: center; color: #8b949e; font-size: 1.1rem; margin-bottom: 2rem;">'
    'Your AI-powered companion for UPSC CSE, State PCS, SSC & other competitive exams</p>',
    unsafe_allow_html=True
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Quick Examples")
    examples = [
        "Explain the basic structure doctrine with key cases",
        "Solve PYQ: Anti-defection law is in which Schedule? (a) 7th (b) 8th (c) 10th",
        "Structure a 250-word Mains answer: Women empowerment in India",
        "Compare FR vs DPSP – landmark judgments",
        "India’s Neighbourhood First Policy – recent developments 2025–26"
    ]

    for ex in examples:
        if st.button(ex, use_container_width=True, key=f"ex_{ex[:30]}"):
            st.session_state.prompt = ex
            st.rerun()

    st.markdown("---")
    st.info(f"Model: **{MODEL_NAME}**  \nRate limits apply — complex questions may take 5–15 seconds.")
    st.caption("Personal project by Adit | Powered by Google Gemini")

# ── Chat history ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role = message["role"]
    css_class = "chat-user" if role == "user" else "chat-ai"
    avatar = "👤" if role == "user" else "🧠"

    with st.chat_message(role, avatar=avatar):
        st.markdown(f'<div class="{css_class}">{message["content"]}</div>', unsafe_allow_html=True)

# ── Input & Generation ───────────────────────────────────────────────────────
if prompt := st.chat_input("Ask your doubt (be specific for best results)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(f'<div class="chat-user">{prompt}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Preparing exam-ready answer..."):
            try:
                system_prompt = """
You are UPSC Insight – elite mentor (former civil servant level) for UPSC/PCS/SSC.
Answer rules:
- 100% accurate, no hallucinations
- Structured: 1. Direct answer 2. Detailed explanation + examples/cases 3. Relevant PYQs 4. Exam tips
- Use bullets, tables, short paragraphs
- Professional Indian English
- Balanced length (400–1200 words)
- Knowledge cutoff: early 2026
"""

                full_prompt = f"{system_prompt}\n\nDoubt: {prompt}"

                response = model.generate_content(full_prompt)
                answer = response.text.strip()

                st.markdown(f'<div class="chat-ai">{answer}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                st.error(f"Error: {str(e)}\nTry again or check model/API key.")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">UPSC Insight © 2026 • Personal project by Adit • Always verify facts from official sources</div>',
    unsafe_allow_html=True
)