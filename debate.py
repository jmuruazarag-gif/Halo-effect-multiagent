import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


def agent_debate_round(cv_json, agent_name, own_evaluation, other_evaluations, previous_round=None, model="openai/gpt-4o-mini"):
    """
    Cada agente revisa su propia evaluación y responde a las opiniones de los demás.
    """

    prompt = f"""
You are {agent_name} in a Deloitte Technology Strategy hiring committee.

You are participating in a multi-agent deliberation about a candidate.

Your task:
- Defend your original evaluation.
- React to the evaluations made by the other agents.
- Mention whether you would revise any view after reading the other evaluations.
- Keep your reasoning consistent with your role.

Return ONLY valid JSON with this structure:

{{
  "agent": "{agent_name}",
  "position_summary": "",
  "response_to_others": "",
  "revised_view": "",
  "proposed_final_decision": "",
  "proposed_hiring_score": 0
}}

Possible final decisions:
- Reject
- Hold
- Interview
- Strong Interview
"""

    user_content = f"""
Candidate CV:
{json.dumps(cv_json, indent=2, ensure_ascii=False)}

Your original evaluation:
{json.dumps(own_evaluation, indent=2, ensure_ascii=False)}

Other agents' evaluations:
{json.dumps(other_evaluations, indent=2, ensure_ascii=False)}

Previous debate round:
{json.dumps(previous_round, indent=2, ensure_ascii=False) if previous_round else "None"}
"""

    response = client.chat.completions.create(
        model=model,
        temperature=0.3,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ]
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("ERROR in debate round:")
        print(content)
        return None


def generate_final_consensus(cv_json, evaluations, debate_round_1, debate_round_2, model="openai/gpt-4o-mini"):
    """
    Genera la decisión final tras dos rondas de deliberación.
    """

    prompt = """
You are the Deloitte Technology Strategy hiring committee.

You have three agents:
- HR Recruiter
- Technology Manager
- Partner

They have completed two rounds of deliberation.

Your task is to produce the final consensus decision of the committee.

Do not simply average the scores. Consider the arguments, disagreements and revised views.

Return ONLY valid JSON with this structure:

{
  "final_decision": "",
  "final_hiring_score": 0,
  "final_strengths": [],
  "final_weaknesses": [],
  "key_disagreements": [],
  "consensus_reasoning": ""
}

Possible final decisions:
- Reject
- Hold
- Interview
- Strong Interview
"""

    user_content = f"""
Candidate CV:
{json.dumps(cv_json, indent=2, ensure_ascii=False)}

Initial individual evaluations:
{json.dumps(evaluations, indent=2, ensure_ascii=False)}

Debate round 1:
{json.dumps(debate_round_1, indent=2, ensure_ascii=False)}

Debate round 2:
{json.dumps(debate_round_2, indent=2, ensure_ascii=False)}
"""

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ]
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("ERROR in final consensus:")
        print(content)
        return None


def run_debate_for_candidate(cv_json, evaluations):
    """
    Ejecuta la deliberación completa para un candidato:
    - Ronda 1
    - Ronda 2
    - Consenso final
    """

    debate_round_1 = []

    for own_eval in evaluations:
        agent_name = own_eval["agent"]

        other_evals = [
            ev for ev in evaluations
            if ev["agent"] != agent_name
        ]

        result = agent_debate_round(
            cv_json=cv_json,
            agent_name=agent_name,
            own_evaluation=own_eval,
            other_evaluations=other_evals
        )

        if result:
            debate_round_1.append(result)

    debate_round_2 = []

    for own_eval in evaluations:
        agent_name = own_eval["agent"]

        other_evals = [
            ev for ev in evaluations
            if ev["agent"] != agent_name
        ]

        result = agent_debate_round(
            cv_json=cv_json,
            agent_name=agent_name,
            own_evaluation=own_eval,
            other_evaluations=other_evals,
            previous_round=debate_round_1
        )

        if result:
            debate_round_2.append(result)

    final_consensus = generate_final_consensus(
        cv_json=cv_json,
        evaluations=evaluations,
        debate_round_1=debate_round_1,
        debate_round_2=debate_round_2
    )

    return {
        "debate_round_1": debate_round_1,
        "debate_round_2": debate_round_2,
        "final_consensus": final_consensus
    }