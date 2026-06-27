import os
import json
import pandas as pd

from agents import AGENTS
from cvs import CVS
from evaluator import evaluate_candidate
from debate import run_debate_for_candidate


def run_individual_evaluations():
    results = []

    os.makedirs("results", exist_ok=True)

    for cv in CVS:
        for agent_name, agent_prompt in AGENTS.items():
            print(f"Evaluating {cv['candidate_id']} with {agent_name}...")

            evaluation = evaluate_candidate(cv, agent_prompt)

            if evaluation is None:
                print(f"Evaluation failed for {cv['candidate_id']} with {agent_name}")
                continue

            evaluation["candidate_id"] = cv["candidate_id"]
            evaluation["candidate_name"] = cv["candidate_name"]
            evaluation["candidate_type"] = cv["candidate_type"]

            results.append(evaluation)

    df = pd.DataFrame(results)
    df.to_csv("results/individual_evaluations.csv", index=False, encoding="utf-8-sig")

    print("Individual evaluations saved.")
    return results


def run_debates(individual_results):
    debate_rows = []
    consensus_rows = []

    for cv in CVS:
        candidate_id = cv["candidate_id"]

        evaluations_for_candidate = [
            evaluation for evaluation in individual_results
            if evaluation["candidate_id"] == candidate_id
        ]

        if len(evaluations_for_candidate) < 3:
            print(f"Skipping debate for {candidate_id}: missing evaluations.")
            continue

        print(f"Running debate for {candidate_id}...")

        debate_result = run_debate_for_candidate(
            cv_json=cv,
            evaluations=evaluations_for_candidate
        )

        round_1 = debate_result["debate_round_1"]
        round_2 = debate_result["debate_round_2"]
        final_consensus = debate_result["final_consensus"]

        for item in round_1:
            item["candidate_id"] = cv["candidate_id"]
            item["candidate_name"] = cv["candidate_name"]
            item["candidate_type"] = cv["candidate_type"]
            item["debate_round"] = 1
            debate_rows.append(item)

        for item in round_2:
            item["candidate_id"] = cv["candidate_id"]
            item["candidate_name"] = cv["candidate_name"]
            item["candidate_type"] = cv["candidate_type"]
            item["debate_round"] = 2
            debate_rows.append(item)

        if final_consensus is not None:
            final_consensus["candidate_id"] = cv["candidate_id"]
            final_consensus["candidate_name"] = cv["candidate_name"]
            final_consensus["candidate_type"] = cv["candidate_type"]
            consensus_rows.append(final_consensus)

    df_debate = pd.DataFrame(debate_rows)
    df_consensus = pd.DataFrame(consensus_rows)

    df_debate.to_csv("results/debate_rounds.csv", index=False, encoding="utf-8-sig")
    df_consensus.to_csv("results/final_consensus.csv", index=False, encoding="utf-8-sig")

    print("Debate rounds saved in results/debate_rounds.csv")
    print("Final consensus saved in results/final_consensus.csv")

    return debate_rows, consensus_rows


if __name__ == "__main__":
    individual_results = run_individual_evaluations()
    run_debates(individual_results)