import streamlit as st
from groq_api import init_groq, generate_mcqs
from pdf_generator import create_assessment_pdf
from pypdf import PdfReader

st.set_page_config(
    page_title="Abhi Gen_AI - Assessment Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}

.glass-header {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 30px 40px;
    margin-bottom: 30px;
    text-align: center;
}

.glass-header h1 {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -1px;
}

.glass-header p {
    color: rgba(255, 255, 255, 0.6);
    font-size: 16px;
    margin-top: 8px;
    font-weight: 300;
}

.glass-card {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 28px 30px;
    margin-bottom: 20px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
}

.glass-card h3 {
    color: #c4b5fd;
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 18px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.glass-card h3::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 20px;
    background: linear-gradient(180deg, #667eea, #764ba2);
    border-radius: 2px;
}

.question-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 20px 24px;
    margin: 14px 0;
    transition: all 0.2s ease;
}

.question-card:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(102, 126, 234, 0.3);
}

.question-card .q-num {
    color: #667eea;
    font-weight: 700;
    font-size: 14px;
}

.question-card .q-type-badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 12px;
    margin-left: 8px;
}

.question-card .q-text {
    color: rgba(255, 255, 255, 0.9);
    font-size: 15px;
    font-weight: 500;
    margin: 6px 0 12px 0;
    line-height: 1.6;
}

.question-card .option {
    color: rgba(255, 255, 255, 0.7);
    font-size: 14px;
    padding: 6px 0 6px 16px;
    border-left: 2px solid rgba(102, 126, 234, 0.2);
    margin: 4px 0;
}

.question-card .correct-badge {
    display: inline-block;
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    margin-top: 8px;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.5) !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3) !important;
}

.stDownloadButton > button:hover {
    box-shadow: 0 8px 30px rgba(16, 185, 129, 0.5) !important;
}

div[data-testid="stTextInput"] > div > input,
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stSlider"] > div,
div[data-testid="stNumberInput"] > div > input {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 10px !important;
    color: rgba(255, 255, 255, 0.9) !important;
}

div[data-testid="stSelectbox"] > div > div {
    padding: 4px 8px !important;
}

label {
    color: rgba(255, 255, 255, 0.7) !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}

div[data-testid="stTextInput"] > div > input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
}

div.stAlert {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    color: rgba(255, 255, 255, 0.8) !important;
}

.stSuccess {
    background: rgba(16, 185, 129, 0.1) !important;
    border: 1px solid rgba(16, 185, 129, 0.2) !important;
}

.stError {
    background: rgba(239, 68, 68, 0.1) !important;
    border: 1px solid rgba(239, 68, 68, 0.2) !important;
}

.stCheckbox {
    color: rgba(255, 255, 255, 0.8) !important;
}

footer { display: none; }
#MainMenu { visibility: hidden; }
</style>
"""

def extract_pdf_text(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return None

TYPE_BADGE_COLORS = {
    "mcq": "#667eea",
    "true_false": "#f59e0b",
    "fill_blanks": "#10b981",
    "short_answer": "#ef4444",
    "match_following": "#8b5cf6"
}

TYPE_LABELS = {
    "mcq": "MCQ",
    "true_false": "True/False",
    "fill_blanks": "Fill Blanks",
    "short_answer": "Short Answer",
    "match_following": "Match"
}

def render_questions(qa):
    for q in qa:
        q_type = q.get("type", "mcq")
        badge_color = TYPE_BADGE_COLORS.get(q_type, "#667eea")
        badge_label = TYPE_LABELS.get(q_type, q_type)

        options_html = ""
        if q_type == "mcq":
            opt_text = " | ".join([f"{k}) {v}" for k, v in q.get("options", {}).items()])
            options_html = f'<div class="option">{opt_text}</div>'

        elif q_type == "true_false":
            opts = q.get("options", {})
            opt_text = " | ".join([f"{k}) {v}" for k, v in opts.items()])
            options_html = f'<div class="option">{opt_text}</div>'

        elif q_type == "fill_blanks":
            options_html = '<div class="option">✏️ Fill in the blank</div>'

        elif q_type == "short_answer":
            options_html = '<div class="option">📝 Write a short answer</div>'

        elif q_type == "match_following":
            pairs = q.get("pairs", {})
            pair_lines = "<br>".join([f"&nbsp;&nbsp;➡ {k} &nbsp;—&nbsp; {v}" for k, v in pairs.items()])
            options_html = f'<div class="option">🔗 Match the following:<br>{pair_lines}</div>'

        correct = q.get("correct_answer", "")
        if q_type == "match_following":
            pairs = q.get("pairs", {})
            pair_str = " → ".join([f"{k}: {v}" for k, v in pairs.items()])
            correct_label = f"✓ Matches: {pair_str}"
        else:
            correct_label = f"✓ Answer: {correct}"

        st.markdown(f"""
        <div class="question-card">
            <div class="q-num">Q{q["id"]} <span class="q-type-badge" style="background:{badge_color}22; color:{badge_color};">{badge_label}</span></div>
            <div class="q-text">{q["question"]}</div>
            {options_html}
            <span class="correct-badge">{correct_label}</span>
        </div>
        """, unsafe_allow_html=True)

def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-header">
        <h1>✨ Abhi Gen_AI</h1>
        <p>AI-Powered Assessment Generator — Create professional quizzes & MCQs in seconds</p>
    </div>
    """, unsafe_allow_html=True)

    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "subject" not in st.session_state:
        st.session_state.subject = ""
    if "topic" not in st.session_state:
        st.session_state.topic = ""
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "Mixed"
    if "question_types" not in st.session_state:
        st.session_state.question_types = ["mcq"]
    if "ref_text" not in st.session_state:
        st.session_state.ref_text = ""

    col1, col2 = st.columns([1, 1.3])

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h3>⚙️ Configuration</h3>", unsafe_allow_html=True)

        api_key = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="sk-...",
            help="Enter your Groq API key from console.groq.com"
        )

        subject = st.text_input("Subject", placeholder="e.g., Physics, History, Data Science")
        topic = st.text_input("Topic", placeholder="e.g., Quantum Mechanics, WW2")

        difficulty = st.selectbox(
            "Difficulty Level",
            options=["Easy", "Medium", "Hard", "Mixed"],
            index=3
        )

        num_questions = st.slider("Number of Questions", min_value=3, max_value=20, value=5)

        st.markdown("<p style='color:rgba(255,255,255,0.7); font-size:14px; font-weight:500; margin:16px 0 6px;'>📌 Question Types</p>", unsafe_allow_html=True)
        q_types_selected = []
        col_a, col_b = st.columns(2)
        with col_a:
            mcq_val = st.checkbox("Multiple Choice", value="mcq" in st.session_state.question_types, key="chk_mcq")
            tf_val = st.checkbox("True/False", value="true_false" in st.session_state.question_types, key="chk_tf")
            fib_val = st.checkbox("Fill in Blanks", value="fill_blanks" in st.session_state.question_types, key="chk_fib")
        with col_b:
            sa_val = st.checkbox("Short Answer", value="short_answer" in st.session_state.question_types, key="chk_sa")
            mt_val = st.checkbox("Match Following", value="match_following" in st.session_state.question_types, key="chk_mt")

        if mcq_val: q_types_selected.append("mcq")
        if tf_val: q_types_selected.append("true_false")
        if fib_val: q_types_selected.append("fill_blanks")
        if sa_val: q_types_selected.append("short_answer")
        if mt_val: q_types_selected.append("match_following")

        if not q_types_selected:
            st.warning("Select at least one question type.")
            q_types_selected = ["mcq"]

        st.markdown("<p style='color:rgba(255,255,255,0.7); font-size:14px; font-weight:500; margin:16px 0 6px;'>📄 Reference PDF (Optional)</p>", unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader("Upload a PDF for the AI to base questions on", type=["pdf"], label_visibility="collapsed")

        ref_text = st.session_state.ref_text
        if uploaded_pdf is not None:
            if "last_pdf" not in st.session_state or st.session_state.last_pdf != uploaded_pdf.name:
                with st.spinner("Extracting text from PDF..."):
                    extracted = extract_pdf_text(uploaded_pdf)
                    if extracted:
                        ref_text = extracted
                        st.session_state.ref_text = extracted
                        st.session_state.last_pdf = uploaded_pdf.name
                        st.success(f"✅ Extracted {len(extracted)} characters from PDF")
                    else:
                        st.error("Failed to extract text from PDF.")
        else:
            st.session_state.ref_text = ""

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h3>🤖 Generate Assessment</h3>", unsafe_allow_html=True)

        generate_clicked = st.button("🚀 Generate Questions", use_container_width=True)

        if generate_clicked:
            if not api_key:
                st.error("Please enter your Groq API key.")
            elif not subject or not topic:
                st.error("Please enter both Subject and Topic.")
            else:
                with st.spinner("Generating questions with Llama 3.1..."):
                    init_groq(api_key)
                    result = generate_mcqs(
                        subject, topic, difficulty, num_questions,
                        question_types=q_types_selected,
                        reference_text=st.session_state.ref_text
                    )

                if "error" in result:
                    st.error(f"❌ {result['error']}")
                    if "raw" in result:
                        with st.expander("Raw Response"):
                            st.code(result["raw"])
                else:
                    st.session_state.questions = result["questions"]
                    st.session_state.subject = subject
                    st.session_state.topic = topic
                    st.session_state.difficulty = difficulty
                    st.session_state.question_types = q_types_selected
                    st.success(f"✅ {result['count']} questions generated successfully!")

        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.questions:
        qs = st.session_state.questions

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"<h3>📋 {st.session_state.subject} — {st.session_state.topic} ({st.session_state.difficulty})</h3>", unsafe_allow_html=True)

        total = len(qs)
        cols = st.columns(3)
        cols[0].metric("Total Questions", total)
        cols[1].metric("Subject", st.session_state.subject)
        cols[2].metric("Difficulty", st.session_state.difficulty)
        st.markdown("</div>", unsafe_allow_html=True)

        render_questions(qs)

        col_left, col_right = st.columns(2)
        with col_left:
            if st.button("🔄 Generate Again", use_container_width=True):
                st.session_state.questions = []
                st.rerun()

        with col_right:
            pdf_buffer = create_assessment_pdf(
                st.session_state.subject,
                st.session_state.topic,
                st.session_state.difficulty,
                qs
            )
            filename = f"{st.session_state.subject}_{st.session_state.topic}_Assessment.pdf".replace(" ", "_")
            st.download_button(
                label="📥 Download PDF",
                data=pdf_buffer,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True
            )

if __name__ == "__main__":
    main()
