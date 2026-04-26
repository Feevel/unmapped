import json
import pandas as pd
from pathlib import Path


# ---------- LOAD DATA (do this once, not inside function if possible) ----------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

relations_df = pd.read_csv(DATA_DIR / "filtered_occupation_skill_relations.csv")

with open(DATA_DIR / "id_map.json", encoding="utf-8") as f:
    skills_db = json.load(f)

# Build fast lookup: skill_id → skill object
skills_lookup = {skill["id"]: skill for skill in skills_db}


# ---------- MAIN FUNCTION ----------

def get_skills_for_occupation(occupation: str):
    """
    Input:
        occupation (str): ESCO occupation preferredLabel

    Returns:
        List[dict]: list of ESCO skill objects (from id_map.json)
    """

    # Normalize input
    occupation = occupation.strip().lower()

    # Filter rows for this occupation
    matches = relations_df[
        relations_df["occupationLabel"].str.lower() == occupation
    ]

    if matches.empty:
        return []

    # Get unique skill URIs
    skill_ids = matches["skillUri"].unique()

    # Map to skill objects (from id_map.json)
    results = []
    for sid in skill_ids:
        skill = skills_lookup.get(sid)
        if skill:
            results.append(skill)

    return results