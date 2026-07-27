import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


def clean_json_response(content):
    content = content.strip()

    if content.startswith("```json"):
        content = content.replace("```json", "").replace("```", "").strip()
    elif content.startswith("```"):
        content = content.replace("```", "").strip()

    return content


def call_llm_json(
    system_prompt,
    user_prompt,
    model="openai/gpt-4o-mini",
    temperature=0.2
):
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    content = clean_json_response(response.choices[0].message.content)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("ERROR: The model did not return valid JSON.")
        print(content)
        return None

def evaluate_candidate_attributes(cv_text, agent_name, agent_prompt):
    system_prompt = f"""
{agent_prompt}

Return ONLY valid JSON with this exact structure:

{{
  "agent": "{agent_name}",

  "technical_competence": 0,
  "technical_justification": "",

  "analytical_thinking": 0,
  "analytical_justification": "",

  "leadership_potential": 0,
  "leadership_justification": "",

  "communication_skills": 0,
  "communication_justification": "",

  "client_facing_ability": 0,
  "client_facing_justification": "",

  "cultural_fit": 0,
  "cultural_fit_justification": "",

  "career_consistency": 0,
  "career_consistency_justification": "",

  "strategic_thinking": 0,
  "strategic_thinking_justification": "",

  "hiring_recommendation": 0,

  "strengths": [],
  "weaknesses": []
}}
"""

    user_prompt = f"""
Candidate CV:

{cv_text}
"""

    return call_llm_json(system_prompt, user_prompt)