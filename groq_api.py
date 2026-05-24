import os
import json
import re
from groq import Groq

client = None

def init_groq(api_key):
    global client
    client = Groq(api_key=api_key)

def generate_mcqs(subject, topic, difficulty, num_questions, question_types=None, reference_text="", additional_instructions=""):
    if not client:
        return {"error": "Groq client not initialized. Provide a valid API key."}

    if not question_types:
        question_types = ["mcq"]

    type_labels = {
        "mcq": "Multiple Choice (4 options A, B, C, D)",
        "true_false": "True/False",
        "fill_blanks": "Fill in the Blanks",
        "short_answer": "Short Answer",
        "match_following": "Match the Following"
    }
    selected_types_str = ", ".join([type_labels[t] for t in question_types if t in type_labels])

    difficulty_prompts = {
        "Easy": f"Generate {num_questions} EASY questions for {subject} focused on '{topic}'. Keep questions basic and straightforward.",
        "Medium": f"Generate {num_questions} MEDIUM-difficulty questions for {subject} focused on '{topic}'. Require conceptual understanding.",
        "Hard": f"Generate {num_questions} HARD questions for {subject} focused on '{topic}'. Require deep analytical thinking and application.",
        "Mixed": f"Generate {num_questions} questions for {subject} focused on '{topic}'. Mix of easy, medium, and hard questions."
    }

    base_prompt = difficulty_prompts.get(difficulty, difficulty_prompts["Mixed"])
    base_prompt += f"\n\nQuestion types to include: {selected_types_str}"

    if reference_text:
        base_prompt += f"\n\nUse the following reference material to base the questions on:\n{reference_text[:5000]}"

    types_schema = r"""
For each question, include a "type" field indicating the question type.

JSON SCHEMA FOR EACH TYPE:

1. Multiple Choice (type: "mcq"):
{
  "id": 1,
  "type": "mcq",
  "question": "What is ...?",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "correct_answer": "A",
  "explanation": "..."
}

2. True/False (type: "true_false"):
{
  "id": 1,
  "type": "true_false",
  "question": "Statement to judge as true or false.",
  "options": {"True": "True", "False": "False"},
  "correct_answer": "True",
  "explanation": "..."
}

3. Fill in the Blanks (type: "fill_blanks"):
{
  "id": 1,
  "type": "fill_blanks",
  "question": "The capital of France is ______.",
  "correct_answer": "Paris",
  "explanation": "..."
}

4. Short Answer (type: "short_answer"):
{
  "id": 1,
  "type": "short_answer",
  "question": "Explain the process of photosynthesis in one sentence.",
  "correct_answer": "Expected answer text",
  "explanation": "Key points that should be covered..."
}

5. Match the Following (type: "match_following"):
{
  "id": 1,
  "type": "match_following",
  "question": "Match the items in Column A with Column B.",
  "pairs": {
    "Item A1": "Item B1",
    "Item A2": "Item B2",
    "Item A3": "Item B3",
    "Item A4": "Item B4"
  },
  "correct_answer": "A1-B1, A2-B2, A3-B3, A4-B4",
  "explanation": "..."
}
"""

    system_prompt = """You are an expert assessment generator for educational content.
Generate high-quality questions in valid JSON format.

Output ONLY valid JSON using this exact structure:
{
  "questions": [
    ...
  ]
}

""" + types_schema + """
Rules:
- Each question must have a "type" field.
- For mcq: exactly 4 options labeled A, B, C, D. correct_answer must be "A", "B", "C", or "D".
- For true_false: options must be {"True": "True", "False": "False"}. correct_answer must be "True" or "False".
- For fill_blanks: use ______ (6 underscores) in the question text to indicate the blank.
- For short_answer: no options field needed. correct_answer is the expected answer.
- For match_following: provide 4 pairs in the "pairs" object. correct_answer can summarize the matches.
- Distribute the questions evenly among the selected types.
- Provide a concise explanation for each correct answer.
- Ensure all questions are unique and relevant.
- Do NOT include any text outside the JSON block."""

    user_prompt = base_prompt
    if additional_instructions:
        user_prompt += f"\n\nAdditional requirements: {additional_instructions}"

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )

        content = response.choices[0].message.content.strip()

        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group()

        data = json.loads(content)
        questions = data.get("questions", [])
        for q in questions:
            if "type" not in q:
                q["type"] = "mcq"
        return {"questions": questions, "count": len(questions)}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse response as JSON: {str(e)}", "raw": content}
    except Exception as e:
        return {"error": f"API error: {str(e)}"}
