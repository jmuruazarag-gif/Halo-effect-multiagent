import os
import pandas as pd

from agents import AGENTS, DELIBERATION_AGENTS
from cvs import CVS
from evaluator import evaluate_candidate_attributes
from debate import run_peer_review_for_candidate, run_committee_consensus_for_candidate


def build_experimental_cases():
    cases = []

    for base_candidate_id, data in CVS.items():
        cases.append({
            "candidate_id": f"{base_candidate_id}_neutral",
            "base_candidate_id": base_candidate_id,
            "candidate_type": "neutral",
            "trigger": data["trigger"],
            "cv_text": data["neutral"]
        })

        cases.append({
            "candidate_id": f"{base_candidate_id}_halo",
            "base_candidate_id": base_candidate_id,
            "candidate_type": "halo",
            "trigger": data["trigger"],
            "cv_text": data["halo"]
        })

    return cases


def add_candidate_metadata(row, case):
    row["candidate_id"] = case["candidate_id"]
    row["base_candidate_id"] = case["base_candidate_id"]
    row["candidate_type"] = case["candidate_type"]
    row["trigger"] = case["trigger"]
    return row


def run_attribute_evaluations(cases):
    results = []

    for case in cases:
        for agent_name, agent_prompt in AGENTS.items():
            print(f"Attribute evaluation: {case['candidate_id']} with {agent_name}...")

            result = evaluate_candidate_attributes(
                cv_text=case["cv_text"],
                agent_name=agent_name,
                agent_prompt=agent_prompt
            )

            if result is None:
                print(f"Attribute evaluation failed for {case['candidate_id']} with {agent_name}")
                continue

            results.append(add_candidate_metadata(result, case))

    df = pd.DataFrame(results)
    df.to_csv("results/attribute_evaluations.csv", index=False, encoding="utf-8-sig", sep=";")

    print("Attribute evaluations saved.")
    return results


def run_peer_reviews(cases, attribute_results):
    all_revised = []

    for case in cases:
        candidate_id = case["candidate_id"]

        evaluations_for_candidate = [
            evaluation for evaluation in attribute_results
            if evaluation["candidate_id"] == candidate_id
        ]

        if len(evaluations_for_candidate) < 3:
            print(f"Skipping peer review for {candidate_id}: missing evaluations.")
            continue

        print(f"Peer review: {candidate_id}...")

        revised = run_peer_review_for_candidate(
            cv_text=case["cv_text"],
            evaluations=evaluations_for_candidate,
            agents=DELIBERATION_AGENTS
        )

        for item in revised:
            all_revised.append(add_candidate_metadata(item, case))

    df = pd.DataFrame(all_revised)
    df.to_csv("results/revised_evaluations.csv", index=False, encoding="utf-8-sig", sep=";")

    print("Revised evaluations saved.")
    return all_revised


def run_committee_consensus(cases, revised_results):
    consensus_rows = []

    for case in cases:
        candidate_id = case["candidate_id"]

        revised_for_candidate = [
            evaluation for evaluation in revised_results
            if evaluation["candidate_id"] == candidate_id
        ]

        if len(revised_for_candidate) < 3:
            print(f"Skipping committee consensus for {candidate_id}: missing revised evaluations.")
            continue

        print(f"Committee consensus: {candidate_id}...")

        consensus = run_committee_consensus_for_candidate(
            cv_text=case["cv_text"],
            revised_evaluations=revised_for_candidate,
            agents=DELIBERATION_AGENTS
        )

        for item in consensus["consensus_round_1"]:
            item["consensus_round"] = 1
            consensus_rows.append(add_candidate_metadata(item, case))

        for item in consensus["consensus_round_2"]:
            item["consensus_round"] = 2
            consensus_rows.append(add_candidate_metadata(item, case))

    df = pd.DataFrame(consensus_rows)
    df.to_csv("results/committee_consensus.csv", index=False, encoding="utf-8-sig", sep=";")

    print("Committee consensus saved.")
    return consensus_rows


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)

    cases = build_experimental_cases()

    attribute_results = run_attribute_evaluations(cases)
    revised_results = run_peer_reviews(cases, attribute_results)
    consensus_results = run_committee_consensus(cases, revised_results)

    print("Full multi-agent evaluation process completed.")