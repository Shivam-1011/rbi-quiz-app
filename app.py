import streamlit as st
import random
from parser import extract_questions

st.set_page_config(page_title="RBI Quiz App", layout="wide")

st.title("RBI Grade B MCQ Quiz")

uploaded_files = st.file_uploader(
    "Upload PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if "questions" not in st.session_state:
    st.session_state.questions = []

if uploaded_files and not st.session_state.questions:

    all_questions = []

    for pdf in uploaded_files:
        all_questions.extend(extract_questions(pdf))

    random.shuffle(all_questions)

    st.session_state.questions = all_questions
    st.session_state.index = 0
    st.session_state.score = 0

if st.session_state.questions:

    q = st.session_state.questions[
        st.session_state.index
    ]

    st.subheader(
        f"Question {st.session_state.index + 1}"
    )

    st.write(q["question"])

    choice = st.radio(
        "Choose Answer",
        list(q["options"].keys()),
        format_func=lambda x:
            f"{x}. {q['options'][x]}"
    )

    if st.button("Submit"):

        if choice == q["answer"]:
            st.success("Correct")
            st.session_state.score += 1
        else:
            st.error(
                f"Wrong. Correct Answer: {q['answer']}"
            )

        st.info(q["explanation"])

    if st.button("Next Question"):

        st.session_state.index += 1

        if st.session_state.index >= len(
            st.session_state.questions
        ):
            st.success(
                f"Quiz Complete! Score: "
                f"{st.session_state.score}/"
                f"{len(st.session_state.questions)}"
            )
        else:
            st.rerun()

    st.sidebar.metric(
        "Score",
        st.session_state.score
    )