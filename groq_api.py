import os
import json
import re
from groq import Groq

client = None

def init_groq(api_key):
    global client
    client = Groq(api_key=api_key)

def generate_mcqs(subject, topic, difficulty, num_questions, additional_instructions=""):
    if not client:
        return {"error": "Groq client not initialized. Provide a valid API key."}

    difficulty_prompts = {
        "Easy": f"Generate {num_questions} EASY multiple-choice questions for {subject} focused on '{topic}'. Keep questions basic and straightforward. Each with 4 options (A, B, C, D).",
        "Medium": f"Generate {num_questions} MEDIUM-difficulty multiple-choice questions for {subject} focused on '{topic}'. Require conceptual understanding. Each with 4 options (A, B, C, D).",
        "Hard": f"Generate {num_questions} HARD multiple-choice questions for {subject} focused on '{topic}'. Require deep analytical thinking and application. Each with 4 options (A, B, C, D).",
        "Mixed": f"Generate {num_questions} multiple-choice questions for {subject} focused on '{topic}'. Mix of easy, medium, and hard questions. Each with 4 options (A, B, C, D)."
    }

    base_prompt = difficulty_prompts.get(difficulty, difficulty_prompts["Mixed"])

    system_prompt = """You are an expert assessment generator for educational content.
Generate high-quality multiple-choice questions in valid JSON format.

Output ONLY valid JSON using this exact structure:
{
  "questions": [
    {
      "id": 1,
      "question": "What is ...?",
      "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
      "correct_answer": "A",
      "explanation": "Brief explanation of why this answer is correct."
    }
  ]
}

Rules:
- Each question must have exactly 4 options labeled A, B, C, D.
- correct_answer must be exactly "A", "B", "C", or "D".
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
        return {"questions": questions, "count": len(questions)}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse response as JSON: {str(e)}", "raw": content}
    except Exception as e:
        return {"error": f"API error: {str(e)}"}
