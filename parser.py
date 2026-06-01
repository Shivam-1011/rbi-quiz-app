import re
import pdfplumber


# --------------------------------------------------
# CLEAN PDF ARTIFACTS
# --------------------------------------------------
def clean_text(text):

    patterns = [
        r'\b\d+\s*\|\s*Page\b\s*\d*',   # 3 | Page
        r'\bPage\s+\d+\b',              # Page 3
        r'^\s*\d+\s*$'                  # Standalone page numbers
    ]

    for pattern in patterns:
        text = re.sub(
            pattern,
            '',
            text,
            flags=re.IGNORECASE | re.MULTILINE
        )

    return text


# --------------------------------------------------
# FORMAT QUESTIONS / EXPLANATIONS
# --------------------------------------------------
def format_question(text):

    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)

    # Numbered statements
    text = re.sub(
        r'\s+(\d+\.)\s+',
        r'\n\1 ',
        text
    )

    # Roman numerals
    text = re.sub(
        r'\s+(\([ivxIVX]+\))\s+',
        r'\n\1 ',
        text
    )

    # Bullet symbols
    text = re.sub(
        r'\s*([•●▪■◦])\s*',
        r'\n\1 ',
        text
    )

    # Statement labels
    text = re.sub(
        r'\s+(Statement\s+\d+)',
        r'\n\1',
        text,
        flags=re.IGNORECASE
    )

    # Remove excessive line breaks
    text = re.sub(r'\n+', '\n', text)

    return text.strip()


# --------------------------------------------------
# EXTRACT QUESTIONS
# --------------------------------------------------
def extract_questions(pdf_file):

    questions = []

    with pdfplumber.open(pdf_file) as pdf:

        text = ""

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                page_text = clean_text(page_text)
                text += "\n" + page_text

    # Split by Q.1), Q.2), etc.
    blocks = re.split(
        r"\nQ\.\d+\)",
        text
    )

    for block in blocks:

        if "Answer:" not in block:
            continue

        try:

            lines = block.strip().split("\n")

            question = ""
            options = {}
            answer = ""
            explanation = ""

            mode = "question"

            for line in lines:

                line = line.strip()

                if not line:
                    continue

                # --------------------
                # OPTIONS
                # --------------------
                option_match = re.match(
                    r"^\[([A-E])\]\s*(.*)",
                    line
                )

                if option_match:

                    mode = "option"

                    options[
                        option_match.group(1)
                    ] = option_match.group(2)

                    continue

                # --------------------
                # ANSWER
                # --------------------
                if line.startswith("Answer:"):

                    answer = (
                        line.replace(
                            "Answer:",
                            ""
                        ).strip()
                    )

                    mode = "answer"
                    continue

                # --------------------
                # EXPLANATION
                # --------------------
                if line.startswith("Explanation:"):

                    explanation = (
                        line.replace(
                            "Explanation:",
                            ""
                        ).strip()
                    )

                    mode = "explanation"
                    continue

                # --------------------
                # QUESTION TEXT
                # --------------------
                if mode == "question":

                    if question:
                        question += " " + line
                    else:
                        question = line

                # --------------------
                # EXPLANATION TEXT
                # --------------------
                elif mode == "explanation":

                    if explanation:
                        explanation += " " + line
                    else:
                        explanation = line

            # ----------------------------
            # FINAL FORMATTING
            # ----------------------------
            question = format_question(question)
            explanation = format_question(explanation)

            # ----------------------------
            # SAVE QUESTION
            # ----------------------------
            if (
                question
                and options
                and answer
            ):

                questions.append({
                    "question": question,
                    "options": options,
                    "answer": answer,
                    "explanation": explanation
                })

        except Exception as e:
            print(f"Error processing question: {e}")

    return questions
