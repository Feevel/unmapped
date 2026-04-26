import json
from pathlib import Path

try:
    import ollama
except ImportError:
    ollama = None

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

model = None
index = None
skills_db = None

# ---------- CACHE ----------

rewrite_cache = {}
store_cache = {}


def _load_store():
    global model, index, skills_db

    if model is not None and index is not None and skills_db is not None:
        return model, index, skills_db

    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index(str(DATA_DIR / "faiss.index"))

    with open(DATA_DIR / "id_map.json", "r", encoding="utf-8") as f:
        skills_db = json.load(f)

    return model, index, skills_db

# ---------- LLM QUERY REWRITE (OLLAMA) ----------

def rewrite_query(user_input: str) -> str:
    if user_input in rewrite_cache:
        return rewrite_cache[user_input]

    if ollama is None:
        rewrite_cache[user_input] = user_input
        return user_input

    prompt = f"""
Extract atomic, professional ESCO-style skills.

Rules:
- Use formal phrasing (e.g. "repair mobile devices")
- 3–6 words per skill
- One skill per item
- No explanations
- Output ONLY comma-separated skills

Input:
{user_input}

Output:
"""

    try:
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception:
        rewrite_cache[user_input] = user_input
        return user_input

    text = response["message"]["content"].strip()

    # cleanup
    text = text.replace("Here are the skills:", "")
    text = text.replace("\n", ",")
    text = text.strip()

    rewrite_cache[user_input] = text
    return text

# ---------- SPLIT SKILLS ----------

def split_skills(text):
    return [s.strip() for s in text.split(",") if len(s.strip()) > 2]

# ---------- KEYWORD SCORING ----------

def keyword_overlap(query, text):
    q_words = set(query.lower().split())
    t_words = set(text.lower().split())

    if not q_words:
        return 0.0

    overlap = len(q_words & t_words)
    return overlap / len(q_words)  # bounded ≤ 1

# ---------- CONFIDENCE ----------

def normalize_score(score, min_s=0.2, max_s=0.9):
    score = max(min(score, max_s), min_s)
    return (score - min_s) / (max_s - min_s)

# ---------- MAIN SEARCH ----------

def search_esco(user_input, k_initial=12, per_skill_top=2, k_final=7):
    model, index, skills_db = _load_store()
    import numpy as np

    # 1. Rewrite input
    rewritten = rewrite_query(user_input)

    # 2. Split into atomic skill queries
    skill_queries = split_skills(rewritten)

    all_candidates = []

    # 3. Retrieve per skill
    for skill_query in skill_queries:
        q_emb = model.encode([skill_query], normalize_embeddings=True)
        q_emb = np.array(q_emb).astype("float32")

        D, I = index.search(q_emb, k_initial)

        local_candidates = []

        for idx, dist in zip(I[0], D[0]):
            skill = skills_db[idx]

            sim = 1 - dist / 2
            text = skill["name"] + " " + skill["description"]
            kw_score = keyword_overlap(skill_query, text)

            final_score = 0.7 * sim + 0.3 * kw_score

            local_candidates.append({
                "id": skill["id"],
                "name": skill["name"],
                "description": skill["description"],
                "score": float(final_score),
                "similarity": float(sim),
                "keyword_score": float(kw_score),
                "source_query": skill_query
            })

        # ✅ KEEP TOP-N PER SKILL (diversity fix)
        local_candidates = sorted(local_candidates, key=lambda x: x["score"], reverse=True)
        all_candidates.extend(local_candidates[:per_skill_top])

    # 4. Deduplicate globally
    unique = {}
    for c in all_candidates:
        if c["id"] not in unique or c["score"] > unique[c["id"]]["score"]:
            unique[c["id"]] = c

    candidates = list(unique.values())

    # 5. Final ranking
    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)

    # 6. Confidence + explanation
    for c in candidates:
        c["confidence"] = round(normalize_score(c["score"]), 3)
        c["explanation"] = f"Matched '{c['name']}' from '{c['source_query']}'"

    return {
        "rewritten_query": rewritten,
        "results": candidates[:k_final]
    }


# ---------- TEST ----------

if __name__ == "__main__":
    test_input = """
    I have repaired phones for 5 years. I replace screens, fix charging ports,
    install apps, talk to customers, buy spare parts, and manage payments.
    I also learned basic coding from YouTube.
    """

    result = search_esco(test_input)
    print(result)
