# -*- coding: utf-8 -*-
"""
Análisis estadístico del experimento de efecto halo.

Archivos generados:
1. 00_candidate_halo_effects.csv
   Efecto halo de cada candidato, promediando los tres agentes.

2. 01_halo_effect.csv
   Resumen del efecto halo directo por modelo, fase, agente y atributo.
   La fila ALL utiliza cinco candidatos como unidades de análisis,
   no quince evaluaciones candidato-agente.

3. 02_peer_review_effect.csv
   Diferencia de diferencias:
       (halo_revisado - neutral_revisado)
       -
       (halo_inicial - neutral_inicial)

4. 03_feeley_intercorrelation.csv
   Intercorrelación media de las dimensiones según Feeley.
   Excluye hiring_recommendation y utiliza la transformación z de Fisher.
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

# Carpeta en la que se encuentra este archivo analysis.py
BASE_DIR = Path(__file__).resolve().parent

# Carpetas con los resultados de cada modelo
MODEL_FOLDERS = {
    "ChatGPT": BASE_DIR / "results" / "results_chatgpt",
    "Claude": BASE_DIR / "results" / "results_claude",
}

INITIAL_FILENAME = "attribute_evaluations.csv"
REVISED_FILENAME = "revised_evaluations.csv"

# Carpeta de salida
OUTPUT_DIR = BASE_DIR / "analysis_results_final"


# Todos los atributos evaluados
ATTRIBUTES = [
    "technical_competence",
    "analytical_thinking",
    "leadership_potential",
    "communication_skills",
    "client_facing_ability",
    "cultural_fit",
    "career_consistency",
    "strategic_thinking",
    "hiring_recommendation",
]


# Para Feeley se excluye hiring_recommendation, porque es una
# decisión global y su inclusión podría elevar artificialmente
# las correlaciones entre dimensiones.
FEELEY_ATTRIBUTES = [
    "technical_competence",
    "analytical_thinking",
    "leadership_potential",
    "communication_skills",
    "client_facing_ability",
    "cultural_fit",
    "career_consistency",
    "strategic_thinking",
]


# Equivalencia entre las columnas revisadas y las iniciales
REVISED_COLUMN_MAPPING = {
    "technical_competence_final": "technical_competence",
    "analytical_thinking_final": "analytical_thinking",
    "leadership_potential_final": "leadership_potential",
    "communication_skills_final": "communication_skills",
    "client_facing_ability_final": "client_facing_ability",
    "cultural_fit_final": "cultural_fit",
    "career_consistency_final": "career_consistency",
    "strategic_thinking_final": "strategic_thinking",
    "hiring_recommendation_final": "hiring_recommendation",
}


# Disparador utilizado en cada candidato
TRIGGER_MAP = {
    "candidate_1_developer":
        "Massachusetts Institute of Technology (MIT)",
    "candidate_2_data_analyst":
        "Solo transatlantic sailing crossing",
    "candidate_3_business_analyst":
        "Summited Mont Blanc",
    "candidate_4_qa_engineer":
        "Marathon des Sables finisher",
    "candidate_5_it_support":
        "Solo coast-to-coast cycling crossing",
}


# Categoría general del disparador
TRIGGER_CATEGORY_MAP = {
    "candidate_1_developer":
        "Academic prestige",
    "candidate_2_data_analyst":
        "Extraordinary personal achievement",
    "candidate_3_business_analyst":
        "Extraordinary personal achievement",
    "candidate_4_qa_engineer":
        "Extraordinary personal achievement",
    "candidate_5_it_support":
        "Extraordinary personal achievement",
}


# ============================================================
# AUXILIARY FUNCTIONS
# ============================================================

def count_positive(values):
    """
    Counts values strictly greater than zero.
    """
    values = pd.Series(values).dropna()
    return int((values > 0).sum())


def count_negative(values):
    """
    Counts values strictly less than zero.
    """
    values = pd.Series(values).dropna()
    return int((values < 0).sum())


def count_zero(values, tolerance=1e-12):
    """
    Counts values that are numerically equal to zero.
    """
    values = pd.Series(values).dropna().to_numpy(dtype=float)

    return int(
        np.isclose(
            values,
            0.0,
            atol=tolerance,
        ).sum()
    )


def fisher_mean(correlations):
    """
    Averages correlations using Fisher's z transformation.

    Correlations equal to -1 or 1 are clipped slightly to avoid
    infinite values in arctanh.
    """
    values = (
        pd.Series(correlations)
        .dropna()
        .to_numpy(dtype=float)
    )

    if len(values) == 0:
        return np.nan

    values = np.clip(
        values,
        -0.999999,
        0.999999,
    )

    fisher_z = np.arctanh(values)
    mean_fisher_z = fisher_z.mean()

    return float(np.tanh(mean_fisher_z))


# ============================================================
# FILE READING AND VALIDATION
# ============================================================

def read_csv_file(path):
    """
    Reads a semicolon-separated CSV file.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    return pd.read_csv(
        path,
        sep=";",
        encoding="utf-8-sig",
    )


def validate_columns(
    df,
    required_columns,
    file_description,
):
    """
    Checks that all required columns exist.
    """
    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in {file_description}: "
            f"{missing_columns}"
        )


def convert_attributes_to_numeric(df):
    """
    Converts all attribute columns to numeric values.
    """
    df = df.copy()

    for attribute in ATTRIBUTES:
        df[attribute] = pd.to_numeric(
            df[attribute],
            errors="coerce",
        )

    return df


def validate_scores(
    df,
    file_description,
):
    """
    Checks that all non-missing scores are between 0 and 10.
    """
    invalid_rows = pd.Series(
        False,
        index=df.index,
    )

    for attribute in ATTRIBUTES:
        invalid_rows = invalid_rows | (
            df[attribute].notna()
            & (
                (df[attribute] < 0)
                | (df[attribute] > 10)
            )
        )

    if invalid_rows.any():
        raise ValueError(
            f"There are scores outside the 0-10 range "
            f"in {file_description}."
        )


def validate_candidate_types(
    df,
    file_description,
):
    """
    Checks that candidate_type contains only neutral or halo.
    """
    valid_types = {
        "neutral",
        "halo",
    }

    observed_types = set(
        df["candidate_type"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
        .unique()
    )

    invalid_types = (
        observed_types
        - valid_types
    )

    if invalid_types:
        raise ValueError(
            f"Invalid candidate_type values in "
            f"{file_description}: {invalid_types}"
        )


def validate_missing_scores(
    df,
    file_description,
):
    """
    Displays a warning if one or more attribute scores are missing
    or could not be converted to numeric values.
    """
    missing_by_attribute = (
        df[ATTRIBUTES]
        .isna()
        .sum()
    )

    missing_by_attribute = missing_by_attribute[
        missing_by_attribute > 0
    ]

    if not missing_by_attribute.empty:
        print(
            f"Warning: missing or non-numeric scores "
            f"in {file_description}:"
        )
        print(
            missing_by_attribute.to_dict()
        )


def prepare_initial_dataset(
    df,
    model_name,
):
    """
    Prepares the initial evaluations.
    """
    required_columns = [
        "candidate_id",
        "base_candidate_id",
        "candidate_type",
        "agent",
    ] + ATTRIBUTES

    validate_columns(
        df,
        required_columns,
        f"{model_name} initial evaluations",
    )

    prepared = df.copy()

    prepared["candidate_type"] = (
        prepared["candidate_type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    prepared["model"] = model_name
    prepared["phase"] = "initial"

    prepared = convert_attributes_to_numeric(
        prepared
    )

    validate_candidate_types(
        prepared,
        f"{model_name} initial evaluations",
    )

    validate_scores(
        prepared,
        f"{model_name} initial evaluations",
    )

    validate_missing_scores(
        prepared,
        f"{model_name} initial evaluations",
    )

    return prepared


def prepare_revised_dataset(
    df,
    model_name,
):
    """
    Prepares the evaluations produced after peer review.
    """
    required_metadata = [
        "candidate_id",
        "base_candidate_id",
        "candidate_type",
        "agent",
    ]

    required_final_columns = list(
        REVISED_COLUMN_MAPPING.keys()
    )

    validate_columns(
        df,
        required_metadata + required_final_columns,
        f"{model_name} revised evaluations",
    )

    prepared = df.rename(
        columns=REVISED_COLUMN_MAPPING
    ).copy()

    prepared["candidate_type"] = (
        prepared["candidate_type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    prepared["model"] = model_name
    prepared["phase"] = "revised"

    prepared = convert_attributes_to_numeric(
        prepared
    )

    validate_candidate_types(
        prepared,
        f"{model_name} revised evaluations",
    )

    validate_scores(
        prepared,
        f"{model_name} revised evaluations",
    )

    validate_missing_scores(
        prepared,
        f"{model_name} revised evaluations",
    )

    return prepared


def load_all_results():
    """
    Loads the initial and revised results for ChatGPT and Claude.
    """
    datasets = []

    for model_name, model_folder in MODEL_FOLDERS.items():

        initial_path = (
            model_folder
            / INITIAL_FILENAME
        )

        revised_path = (
            model_folder
            / REVISED_FILENAME
        )

        if not initial_path.exists():
            print(
                f"Skipping {model_name}: "
                f"{initial_path} was not found."
            )
            continue

        if not revised_path.exists():
            print(
                f"Skipping {model_name}: "
                f"{revised_path} was not found."
            )
            continue

        print(
            f"Reading {model_name} "
            f"initial evaluations..."
        )

        initial_df = read_csv_file(
            initial_path
        )

        initial_df = prepare_initial_dataset(
            initial_df,
            model_name,
        )

        print(
            f"Reading {model_name} "
            f"revised evaluations..."
        )

        revised_df = read_csv_file(
            revised_path
        )

        revised_df = prepare_revised_dataset(
            revised_df,
            model_name,
        )

        datasets.extend([
            initial_df,
            revised_df,
        ])

    if not datasets:
        raise FileNotFoundError(
            "No valid ChatGPT or Claude "
            "results were found."
        )

    return pd.concat(
        datasets,
        ignore_index=True,
    )


# ============================================================
# DIRECT PAIRED HALO EFFECT
# ============================================================

def calculate_paired_halo_effects(df):
    """
    Creates a paired comparison between each neutral CV and
    its halo version for every model, phase, candidate, agent
    and attribute.

    Halo effect:
        halo score - neutral score
    """
    long_df = df.melt(
        id_vars=[
            "model",
            "phase",
            "base_candidate_id",
            "candidate_type",
            "agent",
        ],
        value_vars=ATTRIBUTES,
        var_name="attribute",
        value_name="score",
    )

    paired = long_df.pivot_table(
        index=[
            "model",
            "phase",
            "base_candidate_id",
            "agent",
            "attribute",
        ],
        columns="candidate_type",
        values="score",
        aggfunc="mean",
    ).reset_index()

    paired.columns.name = None

    if "neutral" not in paired.columns:
        paired["neutral"] = np.nan

    if "halo" not in paired.columns:
        paired["halo"] = np.nan

    paired = paired.rename(
        columns={
            "neutral": "neutral_score",
            "halo": "halo_score",
        }
    )

    incomplete_pairs = paired[
        paired["neutral_score"].isna()
        | paired["halo_score"].isna()
    ]

    if not incomplete_pairs.empty:
        print(
            "Warning: some neutral-halo pairs "
            "are incomplete and will not be used."
        )

    paired = paired.dropna(
        subset=[
            "neutral_score",
            "halo_score",
        ]
    ).copy()

    paired["halo_effect"] = (
        paired["halo_score"]
        - paired["neutral_score"]
    )

    paired["trigger"] = (
        paired["base_candidate_id"]
        .map(TRIGGER_MAP)
        .fillna("Unknown trigger")
    )

    paired["trigger_category"] = (
        paired["base_candidate_id"]
        .map(TRIGGER_CATEGORY_MAP)
        .fillna("Unknown category")
    )

    return paired


def create_candidate_halo_effects(
    paired_effects,
):
    """
    Creates the candidate-level dataset.

    The three agents are averaged within each candidate.
    Therefore, each model-phase-attribute combination contains
    five candidate observations, rather than fifteen
    candidate-agent observations.
    """
    candidate_effects = (
        paired_effects
        .groupby(
            [
                "model",
                "phase",
                "base_candidate_id",
                "trigger",
                "trigger_category",
                "attribute",
            ],
            as_index=False,
        )
        .agg(
            mean_neutral_score=(
                "neutral_score",
                "mean"
            ),
            mean_halo_score=(
                "halo_score",
                "mean"
            ),
            mean_halo_effect=(
                "halo_effect",
                "mean"
            ),
            minimum_agent_effect=(
                "halo_effect",
                "min"
            ),
            maximum_agent_effect=(
                "halo_effect",
                "max"
            ),
            agent_effect_sd=(
                "halo_effect",
                "std"
            ),
            positive_agents=(
                "halo_effect",
                count_positive
            ),
            no_change_agents=(
                "halo_effect",
                count_zero
            ),
            negative_agents=(
                "halo_effect",
                count_negative
            ),
            number_of_agents=(
                "halo_effect",
                "count"
            ),
        )
    )

    candidate_effects[
        "effect_direction"
    ] = np.select(
        [
            candidate_effects[
                "mean_halo_effect"
            ] > 0,

            candidate_effects[
                "mean_halo_effect"
            ] < 0,
        ],
        [
            "Positive halo difference",
            "Negative halo difference",
        ],
        default="No halo difference",
    )

    return candidate_effects.sort_values(
        by=[
            "model",
            "phase",
            "base_candidate_id",
            "attribute",
        ]
    )


def create_halo_effect_summary(
    paired_effects,
    candidate_effects,
):
    """
    Summarises the direct halo effect.

    Individual agent rows:
        five candidate pairs for each agent.

    ALL row:
        five candidate-level observations after averaging
        the three agents within each candidate.
    """
    agent_summary = (
        paired_effects
        .groupby(
            [
                "model",
                "phase",
                "agent",
                "attribute",
            ],
            as_index=False,
        )
        .agg(
            mean_neutral_score=(
                "neutral_score",
                "mean"
            ),
            mean_halo_score=(
                "halo_score",
                "mean"
            ),
            mean_halo_effect=(
                "halo_effect",
                "mean"
            ),
            median_halo_effect=(
                "halo_effect",
                "median"
            ),
            minimum_halo_effect=(
                "halo_effect",
                "min"
            ),
            maximum_halo_effect=(
                "halo_effect",
                "max"
            ),
            halo_effect_sd=(
                "halo_effect",
                "std"
            ),
            positive_pairs=(
                "halo_effect",
                count_positive
            ),
            no_change_pairs=(
                "halo_effect",
                count_zero
            ),
            negative_pairs=(
                "halo_effect",
                count_negative
            ),
            number_of_pairs=(
                "halo_effect",
                "count"
            ),
        )
    )

    overall_summary = (
        candidate_effects
        .groupby(
            [
                "model",
                "phase",
                "attribute",
            ],
            as_index=False,
        )
        .agg(
            mean_neutral_score=(
                "mean_neutral_score",
                "mean"
            ),
            mean_halo_score=(
                "mean_halo_score",
                "mean"
            ),
            mean_halo_effect=(
                "mean_halo_effect",
                "mean"
            ),
            median_halo_effect=(
                "mean_halo_effect",
                "median"
            ),
            minimum_halo_effect=(
                "mean_halo_effect",
                "min"
            ),
            maximum_halo_effect=(
                "mean_halo_effect",
                "max"
            ),
            halo_effect_sd=(
                "mean_halo_effect",
                "std"
            ),
            positive_pairs=(
                "mean_halo_effect",
                count_positive
            ),
            no_change_pairs=(
                "mean_halo_effect",
                count_zero
            ),
            negative_pairs=(
                "mean_halo_effect",
                count_negative
            ),
            number_of_pairs=(
                "mean_halo_effect",
                "count"
            ),
        )
    )

    overall_summary["agent"] = "ALL"

    overall_summary = overall_summary[
        agent_summary.columns
    ]

    summary = pd.concat(
        [
            overall_summary,
            agent_summary,
        ],
        ignore_index=True,
    )

    summary[
        "effect_direction"
    ] = np.select(
        [
            summary[
                "mean_halo_effect"
            ] > 0,

            summary[
                "mean_halo_effect"
            ] < 0,
        ],
        [
            "Average positive halo difference",
            "Average negative halo difference",
        ],
        default="No average halo difference",
    )

    return summary.sort_values(
        by=[
            "model",
            "phase",
            "agent",
            "attribute",
        ]
    )


# ============================================================
# PEER REVIEW EFFECT
# ============================================================

def calculate_peer_review_change(
    paired_effects,
):
    """
    Compares the direct halo effect before and after peer review.

    Peer-review change:
        revised halo effect - initial halo effect

    Negative:
        peer review reduces halo.

    Zero:
        peer review does not change halo.

    Positive:
        peer review amplifies halo.
    """
    comparison = paired_effects.pivot_table(
        index=[
            "model",
            "base_candidate_id",
            "agent",
            "attribute",
            "trigger",
            "trigger_category",
        ],
        columns="phase",
        values="halo_effect",
        aggfunc="mean",
    ).reset_index()

    comparison.columns.name = None

    if "initial" not in comparison.columns:
        comparison["initial"] = np.nan

    if "revised" not in comparison.columns:
        comparison["revised"] = np.nan

    comparison = comparison.rename(
        columns={
            "initial":
                "initial_halo_effect",
            "revised":
                "revised_halo_effect",
        }
    )

    comparison = comparison.dropna(
        subset=[
            "initial_halo_effect",
            "revised_halo_effect",
        ]
    ).copy()

    comparison["peer_review_change"] = (
        comparison["revised_halo_effect"]
        - comparison["initial_halo_effect"]
    )

    return comparison


def create_candidate_peer_review_change(
    peer_review_change,
):
    """
    Averages the three agents within each candidate before
    creating the ALL peer-review summary.
    """
    return (
        peer_review_change
        .groupby(
            [
                "model",
                "base_candidate_id",
                "trigger",
                "trigger_category",
                "attribute",
            ],
            as_index=False,
        )
        .agg(
            initial_halo_effect=(
                "initial_halo_effect",
                "mean"
            ),
            revised_halo_effect=(
                "revised_halo_effect",
                "mean"
            ),
            peer_review_change=(
                "peer_review_change",
                "mean"
            ),
        )
    )


def create_peer_review_summary(
    peer_review_change,
    candidate_peer_review,
):
    """
    Summarises whether peer review reduces or amplifies halo.

    Individual agent rows:
        five candidate pairs for each agent.

    ALL row:
        five candidate-level observations after averaging
        the three agents within each candidate.
    """
    agent_summary = (
        peer_review_change
        .groupby(
            [
                "model",
                "agent",
                "attribute",
            ],
            as_index=False,
        )
        .agg(
            mean_initial_halo_effect=(
                "initial_halo_effect",
                "mean"
            ),
            mean_revised_halo_effect=(
                "revised_halo_effect",
                "mean"
            ),
            mean_peer_review_change=(
                "peer_review_change",
                "mean"
            ),
            median_peer_review_change=(
                "peer_review_change",
                "median"
            ),
            minimum_peer_review_change=(
                "peer_review_change",
                "min"
            ),
            maximum_peer_review_change=(
                "peer_review_change",
                "max"
            ),
            peer_review_change_sd=(
                "peer_review_change",
                "std"
            ),
            reductions=(
                "peer_review_change",
                count_negative
            ),
            no_changes=(
                "peer_review_change",
                count_zero
            ),
            amplifications=(
                "peer_review_change",
                count_positive
            ),
            number_of_pairs=(
                "peer_review_change",
                "count"
            ),
        )
    )

    overall_summary = (
        candidate_peer_review
        .groupby(
            [
                "model",
                "attribute",
            ],
            as_index=False,
        )
        .agg(
            mean_initial_halo_effect=(
                "initial_halo_effect",
                "mean"
            ),
            mean_revised_halo_effect=(
                "revised_halo_effect",
                "mean"
            ),
            mean_peer_review_change=(
                "peer_review_change",
                "mean"
            ),
            median_peer_review_change=(
                "peer_review_change",
                "median"
            ),
            minimum_peer_review_change=(
                "peer_review_change",
                "min"
            ),
            maximum_peer_review_change=(
                "peer_review_change",
                "max"
            ),
            peer_review_change_sd=(
                "peer_review_change",
                "std"
            ),
            reductions=(
                "peer_review_change",
                count_negative
            ),
            no_changes=(
                "peer_review_change",
                count_zero
            ),
            amplifications=(
                "peer_review_change",
                count_positive
            ),
            number_of_pairs=(
                "peer_review_change",
                "count"
            ),
        )
    )

    overall_summary["agent"] = "ALL"

    overall_summary = overall_summary[
        agent_summary.columns
    ]

    summary = pd.concat(
        [
            overall_summary,
            agent_summary,
        ],
        ignore_index=True,
    )

    summary["interpretation"] = np.select(
        [
            summary[
                "mean_peer_review_change"
            ] < 0,

            summary[
                "mean_peer_review_change"
            ] > 0,
        ],
        [
            "Peer review reduced halo",
            "Peer review amplified halo",
        ],
        default=(
            "Peer review did not change halo"
        ),
    )

    return summary.sort_values(
        by=[
            "model",
            "agent",
            "attribute",
        ]
    )


# ============================================================
# FEELEY INTERCORRELATION ANALYSIS
# ============================================================

def average_dimension_intercorrelation(
    subset,
):
    """
    Calculates the average Pearson correlation between all
    pairs of evaluation dimensions.

    Correlations are calculated across the five candidates
    evaluated by the same agent and condition.

    hiring_recommendation is excluded.

    Individual correlations are averaged using Fisher's
    z transformation.
    """
    if len(subset) < 3:
        return np.nan

    correlation_matrix = subset[
        FEELEY_ATTRIBUTES
    ].corr(
        method="pearson"
    )

    upper_triangle_mask = np.triu(
        np.ones(
            correlation_matrix.shape,
            dtype=bool,
        ),
        k=1,
    )

    correlation_values = (
        correlation_matrix
        .where(upper_triangle_mask)
        .stack()
        .dropna()
        .to_numpy(dtype=float)
    )

    return fisher_mean(
        correlation_values
    )


def calculate_feeley_intercorrelations(
    df,
):
    """
    Calculates Feeley's average intercorrelation for each:

    - model
    - phase
    - agent
    - candidate condition

    Each agent value is based on five candidates.

    The ALL row averages the three agent-level correlations
    using Fisher's z transformation.
    """
    agent_rows = []

    grouped = df.groupby(
        [
            "model",
            "phase",
            "agent",
            "candidate_type",
        ]
    )

    for (
        model_name,
        phase_name,
        agent_name,
        candidate_type,
    ), subset in grouped:

        agent_rows.append({
            "model": model_name,
            "phase": phase_name,
            "agent": agent_name,
            "candidate_type": candidate_type,
            "average_intercorrelation":
                average_dimension_intercorrelation(
                    subset
                ),
            "number_of_candidates":
                subset[
                    "base_candidate_id"
                ].nunique(),
            "number_of_agents": 1,
        })

    agent_values = pd.DataFrame(
        agent_rows
    )

    if agent_values.empty:
        return pd.DataFrame()

    overall_rows = []

    overall_grouped = agent_values.groupby(
        [
            "model",
            "phase",
            "candidate_type",
        ]
    )

    for (
        model_name,
        phase_name,
        candidate_type,
    ), subset in overall_grouped:

        overall_rows.append({
            "model": model_name,
            "phase": phase_name,
            "agent": "ALL",
            "candidate_type": candidate_type,
            "average_intercorrelation":
                fisher_mean(
                    subset[
                        "average_intercorrelation"
                    ]
                ),
            "number_of_candidates":
                int(
                    subset[
                        "number_of_candidates"
                    ].max()
                ),
            "number_of_agents":
                int(
                    subset["agent"].nunique()
                ),
        })

    overall_values = pd.DataFrame(
        overall_rows
    )

    all_values = pd.concat(
        [
            overall_values,
            agent_values,
        ],
        ignore_index=True,
    )

    comparison = all_values.pivot_table(
        index=[
            "model",
            "phase",
            "agent",
            "number_of_candidates",
            "number_of_agents",
        ],
        columns="candidate_type",
        values="average_intercorrelation",
        aggfunc="mean",
    ).reset_index()

    comparison.columns.name = None

    if "neutral" not in comparison.columns:
        comparison["neutral"] = np.nan

    if "halo" not in comparison.columns:
        comparison["halo"] = np.nan

    comparison = comparison.rename(
        columns={
            "neutral":
                "neutral_average_intercorrelation",
            "halo":
                "halo_average_intercorrelation",
        }
    )

    comparison[
        "intercorrelation_difference"
    ] = (
        comparison[
            "halo_average_intercorrelation"
        ]
        - comparison[
            "neutral_average_intercorrelation"
        ]
    )

    comparison["interpretation"] = np.select(
        [
            comparison[
                "intercorrelation_difference"
            ] > 0,

            comparison[
                "intercorrelation_difference"
            ] < 0,
        ],
        [
            (
                "Attributes were more "
                "intercorrelated with halo"
            ),
            (
                "Attributes were less "
                "intercorrelated with halo"
            ),
        ],
        default=(
            "No difference in intercorrelation"
        ),
    )

    return comparison.sort_values(
        by=[
            "model",
            "phase",
            "agent",
        ]
    )


# ============================================================
# SAVE RESULTS
# ============================================================

def save_result(
    df,
    filename,
):
    """
    Saves a CSV using:

    - semicolon as separator;
    - comma as decimal separator;
    - UTF-8 with BOM.

    This format is compatible with Spanish Excel.
    """
    output_path = (
        OUTPUT_DIR
        / filename
    )

    result = df.copy()

    numeric_columns = (
        result.select_dtypes(
            include=["number"]
        ).columns
    )

    result[numeric_columns] = (
        result[numeric_columns]
        .round(4)
    )

    result.to_csv(
        output_path,
        index=False,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
    )

    print(
        f"Saved: {output_path}"
    )


# ============================================================
# MAIN
# ============================================================

def main():
    """
    Runs the complete analysis.
    """
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "Loading ChatGPT and Claude results..."
    )

    all_results = load_all_results()

    print(
        "Calculating direct neutral-halo "
        "differences..."
    )

    paired_effects = (
        calculate_paired_halo_effects(
            all_results
        )
    )

    candidate_effects = (
        create_candidate_halo_effects(
            paired_effects
        )
    )

    halo_effect_summary = (
        create_halo_effect_summary(
            paired_effects,
            candidate_effects,
        )
    )

    print(
        "Calculating the effect "
        "of peer review..."
    )

    peer_review_change = (
        calculate_peer_review_change(
            paired_effects
        )
    )

    candidate_peer_review = (
        create_candidate_peer_review_change(
            peer_review_change
        )
    )

    peer_review_summary = (
        create_peer_review_summary(
            peer_review_change,
            candidate_peer_review,
        )
    )

    print(
        "Calculating Feeley "
        "intercorrelations..."
    )

    feeley_intercorrelations = (
        calculate_feeley_intercorrelations(
            all_results
        )
    )

    save_result(
        paired_effects,
        "00_agent_candidate_halo_effects.csv",
    )

    save_result(
        candidate_effects,
        "00_candidate_halo_effects.csv",
    )

    save_result(
        halo_effect_summary,
        "01_halo_effect.csv",
    )

    save_result(
        peer_review_summary,
        "02_peer_review_effect.csv",
    )

    save_result(
        feeley_intercorrelations,
        "03_feeley_intercorrelation.csv",
    )

    print()
    print(
        "Analysis completed successfully."
    )
    print()
    print("Final files:")
    print(
        "1. 00_agent_candidate_halo_effects.csv"
    )
    print(
        "2. 00_candidate_halo_effects.csv"
    )
    print(
        "3. 01_halo_effect.csv"
    )
    print(
        "4. 02_peer_review_effect.csv"
    )
    print(
        "5. 03_feeley_intercorrelation.csv"
    )


if __name__ == "__main__":
    main()