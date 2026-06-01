import re
import pdfplumber


# --------------------------------------------------
# CLEAN PDF ARTIFACTS
# --------------------------------------------------
def clean_text(text):

    patterns = [
        r'\b\d+\s*\|\s*Page\b\s*\d*',  # 3 | Page
        r'\bPage\s+\d+\b',             # Page 3
        r'^\s*\d+\s*$'                 # standalone page numbers
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
# FORMAT QUESTIONS
# --------------------------------------------------
def format_question(text):

    # Remove extra spaces but preserve line structure
    text = re.sub(r'\s+', ' ', text)

    # Numbered statements
    text = re.sub(
        r'(?<!\n)(\d+\.)',
        r'\n\n\1',
        text
    )

    # Roman numerals
    text = re.sub(
        r'(?<!\n)(\([ivxIVX]+\))',
        r'\n\n\1',
        text
    )

    # Bullets
    text = re.sub(
        r'(?<!\n)([•●▪■◦])',
        r'\n\n\1',
        text
    )

    # Statement labels
    text = re.sub(
        r'(?<!\n)(Statement\s+\d+)',
        r'\n\n\1',
        text,
        flags=re.IGNORECASE
    )

    # Remove excessive blank lines
    text = re.sub(
        r'\n{3,}',
        '\n\n',
        text
    )

    return text.strip()


# --------------------------------------------------
# EXTRACT QUESTIONS
# --------------------------------------------------
def extract_questions(pdf_file):

    questions = []

    # ----------------------------
    # Read PDF
    # ----------------------------
    with pdfplumber.open(pdf_file) as pdf:

        text = ""

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                page_text = clean_text(page_text)
                text += "\n" + page_text

    # ----------------------------
    # Split Questions
    # Example:
    # Q.1)
    # Q.2)
    # ----------------------------
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
                # Options
                # [A] option text
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
                # Answer
                # --------------------
                if line.startswith("Answer:"):

                    answer = (
                        line.replace(
                            "Answer:",
                            ""
                        )
                        .strip()
                    )

                    mode = "answer"
                    continue

                # --------------------
                # Explanation
                # --------------------
                if line.startswith("Explanation:"):

                    explanation += (
                        line.replace(
                            "Explanation:",
                            ""
                        )
                        .strip()
                    )

                    mode = "explanation"
                    continue

                # --------------------
                # Question text
                # --------------------
                if mode == "question":

                    question += " " + line

                # --------------------
                # Explanation text
                # --------------------
                elif mode == "explanation":

                    explanation += " " + line

            # ----------------------------
            # Final formatting
            # ----------------------------
            question = format_question(
                question
            )

            explanation = format_question(
                explanation
            )

            # ----------------------------
            # Save Question
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

        except Exception:
            pass

    return questions
