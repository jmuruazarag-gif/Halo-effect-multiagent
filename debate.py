import json
from evaluator import call_llm_json


def revise_evaluation_after_peer_review(
    cv_text,
    agent_name,
    agent_prompt,
    own_evaluation,
    peer_evaluations
):
    system_prompt = f"""
{agent_prompt}

You must now revise your evaluation after reading the other committee members' scores and justifications.

Important rules:
- Keep your own role perspective.
- You may revise a score if the other agents' arguments make you reinterpret the CV evidence.
- Do not revise only to agree with the others.
- If you change a score, explain why.
- If you keep a score, explain briefly why.

Return ONLY valid JSON with this exact structure:

{{
  "agent": "{agent_name}",

  "technical_competence_final": 0,
  "technical_change_reason": "",

  "analytical_thinking_final": 0,
  "analytical_change_reason": "",

  "leadership_potential_final": 0,
  "leadership_change_reason": "",

  "communication_skills_final": 0,
  "communication_change_reason": "",

  "client_facing_ability_final": 0,
  "client_facing_change_reason": "",

  "cultural_fit_final": 0,
  "cultural_fit_change_reason": "",

  "career_consistency_final": 0,
  "career_consistency_change_reason": "",

  "strategic_thinking_final": 0,
  "strategic_thinking_change_reason": "",

  "hiring_recommendation_final": 0,
  "hiring_change_reason": "",

  "changed_attributes": [],
  "overall_revision_summary": ""
}}
"""

    user_prompt = f"""
Candidate CV:

{cv_text}

Your original evaluation:

{json.dumps(own_evaluation, indent=2, ensure_ascii=False)}

Other committee members' evaluations:

{json.dumps(peer_evaluations, indent=2, ensure_ascii=False)}
"""

    return call_llm_json(system_prompt, user_prompt, temperature=0.3)


def committee_consensus_round(
    cv_text,
    agent_name,
    agent_prompt,
    own_revised_evaluation,
    peer_revised_evaluations,
    previous_consensus_round=None
):
    system_prompt = f"""
{agent_prompt}

You are now in the final consensus stage of the hiring committee.

There is no external judge.
The final committee decision must emerge from the three agents.

Your task:
- Review your revised evaluation.
- Review the revised evaluations of the other agents.
- Try to reach a shared committee decision.
- You may support the committee decision even if you still have minor disagreements.

Return ONLY valid JSON with this exact structure:

{{
  "agent": "{agent_name}",
  "committee_decision": "",
  "final_hiring_recommendation": 0,
  "consensus_position": "",
  "main_reasoning": "",
  "remaining_disagreements": [],
  "willing_to_support_committee_decision": true
}}

Possible committee_decision values:
- Reject
- Hold
- Interview
- Strong Interview
"""

    user_prompt = f"""
Candidate CV:

{cv_text}

Your revised evaluation:

{json.dumps(own_revised_evaluation, indent=2, ensure_ascii=False)}

Other agents' revised evaluations:

{json.dumps(peer_revised_evaluations, indent=2, ensure_ascii=False)}

Previous consensus round:

{json.dumps(previous_consensus_round, indent=2, ensure_ascii=False) if previous_consensus_round else "None"}
"""

    return call_llm_json(system_prompt, user_prompt, temperature=0.3)


def run_peer_review_for_candidate(cv_text, evaluations, agents):
    revised_evaluations = []

    for own_eval in evaluations:
        agent_name = own_eval["agent"]
        agent_prompt = agents[agent_name]

        peer_evals = [
            ev for ev in evaluations
            if ev["agent"] != agent_name
        ]

        revised = revise_evaluation_after_peer_review(
            cv_text=cv_text,
            agent_name=agent_name,
            agent_prompt=agent_prompt,
            own_evaluation=own_eval,
            peer_evaluations=peer_evals
        )

        if revised:
            revised_evaluations.append(revised)

    return revised_evaluations


def run_committee_consensus_for_candidate(cv_text, revised_evaluations, agents):
    consensus_round_1 = []

    for own_revised in revised_evaluations:
        agent_name = own_revised["agent"]
        agent_prompt = agents[agent_name]

        peer_revised = [
            ev for ev in revised_evaluations
            if ev["agent"] != agent_name
        ]

        result = committee_consensus_round(
            cv_text=cv_text,
            agent_name=agent_name,
            agent_prompt=agent_prompt,
            own_revised_evaluation=own_revised,
            peer_revised_evaluations=peer_revised
        )

        if result:
            consensus_round_1.append(result)

    consensus_round_2 = []

    for own_revised in revised_evaluations:
        agent_name = own_revised["agent"]
        agent_prompt = agents[agent_name]

        peer_revised = [
            ev for ev in revised_evaluations
            if ev["agent"] != agent_name
        ]

        result = committee_consensus_round(
            cv_text=cv_text,
            agent_name=agent_name,
            agent_prompt=agent_prompt,
            own_revised_evaluation=own_revised,
            peer_revised_evaluations=peer_revised,
            previous_consensus_round=consensus_round_1
        )

        if result:
            consensus_round_2.append(result)

    return {
        "consensus_round_1": consensus_round_1,
        "consensus_round_2": consensus_round_2
    }