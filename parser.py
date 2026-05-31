import re
import pdfplumber

def extract_questions(pdf_file):
    questions = []

    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += "\n" + t

    blocks = re.split(r"\nQ\.\d+\)", text)

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

                if re.match(r"^\[[A-E]\]", line):
                    mode = "option"
                    m = re.match(r"^\[([A-E])\]\s*(.*)", line)
                    if m:
                        options[m.group(1)] = m.group(2)

                elif line.startswith("Answer:"):
                    answer = line.replace("Answer:", "").strip()
                    mode = "answer"

                elif line.startswith("Explanation:"):
                    explanation += line.replace("Explanation:", "").strip()
                    mode = "explanation"

                else:
                    if mode == "question":
                        question += " " + line
                    elif mode == "explanation":
                        explanation += " " + line

            if question and options and answer:
                questions.append({
                    "question": question,
                    "options": options,
                    "answer": answer,
                    "explanation": explanation
                })

        except:
            pass

    return questions