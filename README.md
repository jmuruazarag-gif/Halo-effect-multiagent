# Halo Effect Multi-Agent Recruitment System

This project implements a multi-agent system to study the halo effect in recruitment decisions using Large Language Models.

## Objective

The system evaluates CVs for a Technology Strategy Analyst position. It compares neutral CVs with halo CVs, where prestige signals such as elite universities, prestigious companies or awards are introduced.

## Architecture

The system includes three evaluator agents:

- HR Recruiter
- Technology Manager
- Partner

Each agent evaluates the same candidate independently using different evaluation criteria.

After the individual evaluations, the agents participate in a two-round debate and then generate a final consensus decision.

## Files

### `agents.py`

Defines the prompts and evaluation criteria for each agent.

### `cvs.py`

Contains the candidate CVs in JSON-like Python dictionaries. It includes neutral CVs and halo CVs.

### `evaluator.py`

Sends each CV to each agent through the OpenRouter API and returns a structured JSON evaluation.

### `debate.py`

Implements the multi-agent deliberation process. Agents participate in two debate rounds and then generate a final consensus.

### `main.py`

Runs the full experiment:
1. Individual evaluations
2. Debate rounds
3. Final consensus
4. Saves results as CSV files

### `.env`

Stores the OpenRouter API key. This file is not uploaded to GitHub.

## Outputs

The system generates:

- `individual_evaluations.csv`
- `debate_rounds.csv`
- `final_consensus.csv`

## How to run

Install dependencies:

```bash
pip install -r requirements.txt