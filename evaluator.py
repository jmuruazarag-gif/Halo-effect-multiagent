import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


def clean_cv_for_model(cv_json):
    """
    Elimina campos internos del experimento para que el agente no sepa
    si el CV es neutral o halo.
    """
    hidden_fields = [
        "candidate_id",
        "candidate_type",
        "base_candidate_id"
    ]

    return {
        key: value
        for key, value in cv_json.items()
        if key not in hidden_fields
    }


def evaluate_candidate(cv_json, agent_prompt, model="openai/gpt-4o-mini"):
    cv_for_model = clean_cv_for_model(cv_json)

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": agent_prompt
            },
            {
                "role": "user",
                "content": f"""
Evaluate the following candidate for the position of Technology Strategy Analyst.

Candidate CV:
{json.dumps(cv_for_model, indent=2, ensure_ascii=False)}
"""
            }
        ]
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)

    except json.JSONDecodeError:
        print("ERROR: The model did not return valid JSON.")
        print("Model response:")
        print(content)
        return None