import streamlit as st
import random
from parser import extract_questions

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="RBI Grade B Quiz",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>
[data-testid="stSidebar"] {
    width: 240px !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
defaults = {
    "questions": [],
    "index": 0,
    "score": 0,
    "answers": {},
    "submitted": {},
    "flagged": set()
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.title("🏦 RBI Grade B MCQ Quiz")

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
uploaded_files = st.file_uploader(
    "Upload PDF Files",
    type=["pdf"],
    accept_multiple_files=True
)

# --------------------------------------------------
# LOAD QUESTIONS
# --------------------------------------------------
if uploaded_files and not st.session_state.questions:

    all_questions = []

    with st.spinner("Extracting questions..."):
        for pdf in uploaded_files:
            all_questions.extend(
                extract_questions(pdf)
            )

    random.shuffle(all_questions)

    st.session_state.questions = all_questions
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.answers = {}
    st.session_state.submitted = {}
    st.session_state.flagged = set()

    st.success(
        f"Loaded {len(all_questions)} questions."
    )

# --------------------------------------------------
# STATUS FUNCTION
# --------------------------------------------------
def get_status(question_no):

    if question_no in st.session_state.flagged:
        return f"🚩{question_no + 1}"

    if question_no in st.session_state.submitted:

        answer = st.session_state.answers.get(
            question_no
        )

        correct_answer = (
            st.session_state.questions[
                question_no
            ]["answer"]
        )

        if answer == correct_answer:
            return f"✅{question_no + 1}"
        else:
            return f"❌{question_no + 1}"

    return f"⬜{question_no + 1}"

# --------------------------------------------------
# QUIZ
# --------------------------------------------------
if st.session_state.questions:

    total_questions = len(
        st.session_state.questions
    )

    current_index = st.session_state.index

    q = st.session_state.questions[
        current_index
    ]

    # ----------------------------------------------
    # PROGRESS BAR
    # ----------------------------------------------
    progress = (
        current_index + 1
    ) / total_questions

    st.progress(progress)

    st.subheader(
        f"Question {current_index + 1} / {total_questions}"
    )

    # ----------------------------------------------
    # QUESTION DISPLAY
    # ----------------------------------------------
    st.text_area(
        "Question",
        q["question"],
        height=250,
        disabled=True
    )

    # ----------------------------------------------
    # OPTIONS
    # ----------------------------------------------
    options = list(
        q["options"].keys()
    )

    saved_answer = (
        st.session_state.answers.get(
            current_index,
            options[0]
        )
    )

    choice = st.radio(
        "Choose Answer",
        options,
        index=options.index(saved_answer),
        format_func=lambda x:
            f"{x}. {q['options'][x]}",
        key=f"radio_{current_index}"
    )

    st.session_state.answers[
        current_index
    ] = choice

    # ----------------------------------------------
    # SUBMIT
    # ----------------------------------------------
    if st.button("Submit Answer"):

        if current_index not in st.session_state.submitted:

            st.session_state.submitted[
                current_index
            ] = True

            if choice == q["answer"]:
                st.session_state.score += 1

        st.rerun()

    # ----------------------------------------------
    # SHOW RESULT
    # ----------------------------------------------
    if current_index in st.session_state.submitted:

        if (
            st.session_state.answers[
                current_index
            ]
            == q["answer"]
        ):
            st.success("✅ Correct Answer")
        else:
            st.error(
                f"❌ Wrong Answer\n\nCorrect Answer: {q['answer']}"
            )

        if q.get("explanation"):

            st.markdown("### Explanation")

            st.text_area(
                "",
                q["explanation"],
                height=150,
                disabled=True,
                key=f"exp_{current_index}"
            )

    # ----------------------------------------------
    # NAVIGATION
    # ----------------------------------------------
    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "⬅ Previous Question"
        ):
            if current_index > 0:
                st.session_state.index -= 1
                st.rerun()

    with col2:

        if st.button(
            "Next Question ➡"
        ):
            if (
                current_index
                < total_questions - 1
            ):
                st.session_state.index += 1
                st.rerun()

    # ----------------------------------------------
    # FINISH QUIZ
    # ----------------------------------------------
    st.divider()

    if st.button("🏁 Finish Quiz"):

        attempted = len(
            st.session_state.submitted
        )

        if attempted > 0:

            accuracy = (
                st.session_state.score
                / attempted
            ) * 100

            st.success(
                f"""
Quiz Complete!

Score: {st.session_state.score}/{total_questions}

Attempted: {attempted}/{total_questions}

Accuracy: {accuracy:.2f}%
"""
            )

        else:
            st.warning(
                "No questions attempted."
            )

    # --------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------
    st.sidebar.title(
        "📊 Quiz Dashboard"
    )

    answered = len(
        st.session_state.submitted
    )

    st.sidebar.metric(
        "Score",
        st.session_state.score
    )

    st.sidebar.metric(
        "Answered",
        answered
    )

    st.sidebar.metric(
        "Remaining",
        total_questions - answered
    )

    st.sidebar.metric(
        "Flagged",
        len(
            st.session_state.flagged
        )
    )

    st.sidebar.divider()

    # ----------------------------------------------
    # JUMP TO QUESTION
    # ----------------------------------------------
    jump_to = st.sidebar.number_input(
        "Jump To Question",
        min_value=1,
        max_value=total_questions,
        value=current_index + 1
    )

    if st.sidebar.button("Go"):

        st.session_state.index = (
            jump_to - 1
        )

        st.rerun()

    st.sidebar.divider()

    # ----------------------------------------------
    # FLAG QUESTION
    # ----------------------------------------------
    if (
        current_index
        in st.session_state.flagged
    ):

        if st.sidebar.button(
            "Remove Flag 🚩"
        ):
            st.session_state.flagged.remove(
                current_index
            )
            st.rerun()

    else:

        if st.sidebar.button(
            "Flag Question 🚩"
        ):
            st.session_state.flagged.add(
                current_index
            )
            st.rerun()

    st.sidebar.divider()

    # ----------------------------------------------
    # FLAGGED QUESTIONS
    # ----------------------------------------------
    if st.session_state.flagged:

        st.sidebar.subheader(
            "🚩 Flagged Questions"
        )

        for q_no in sorted(
            st.session_state.flagged
        ):

            if st.sidebar.button(
                f"Question {q_no + 1}",
                key=f"flag_{q_no}"
            ):

                st.session_state.index = q_no
                st.rerun()

    st.sidebar.divider()

    # ----------------------------------------------
    # QUESTION NAVIGATOR
    # ----------------------------------------------
    st.sidebar.subheader(
        "Question Navigator"
    )

    cols = st.sidebar.columns(5)

    for i in range(total_questions):

        with cols[i % 5]:

            if st.button(
                get_status(i),
                key=f"nav_{i}"
            ):

                st.session_state.index = i
                st.rerun()

else:

    st.info(
        "Upload one or more PDF files to start the quiz."
    )
