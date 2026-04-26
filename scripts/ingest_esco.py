import pandas as pd
import json
import re
import numpy as np
import faiss
from tqdm import tqdm
import os
from sentence_transformers import SentenceTransformer

# ========= PATH SETUP =========

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKILLS_CSV = os.path.join(BASE_DIR, "data", "skills_en.csv")

FAISS_INDEX_PATH = os.path.join(BASE_DIR, "data", "faiss.index")
ID_MAP_PATH = os.path.join(BASE_DIR, "data", "id_map.json")

# ========= LOAD MODEL =========

print("Loading local embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# ========= HELPERS =========

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def is_valid_skill(name, desc):
    # minimal cleaning only (no aggressive filtering)
    if len(name.strip()) == 0:
        return False
    return True


# ========= STEP 1: LOAD =========

print("Loading ESCO skills...")
df = pd.read_csv(SKILLS_CSV)

df = df[["conceptUri", "preferredLabel", "description"]]

# ========= STEP 2: CLEAN =========

print("Cleaning data...")
cleaned = []

for _, row in df.iterrows():
    name = clean_text(row["preferredLabel"])
    desc = clean_text(row["description"])

    if not is_valid_skill(name, desc):
        continue

    cleaned.append({
        "id": row["conceptUri"],
        "name": name,
        "description": desc
    })

print(f"Total skills loaded: {len(cleaned)}")

# ========= STEP 3: PREPARE TEXT =========

texts = [
    s["name"] + ". " + s["description"]
    for s in cleaned
]

# ========= STEP 4: EMBEDDINGS =========

print("Creating embeddings...")

embeddings = []

BATCH_SIZE = 128

for i in tqdm(range(0, len(texts), BATCH_SIZE)):
    batch = texts[i:i+BATCH_SIZE]
    emb = model.encode(batch, normalize_embeddings=True)
    embeddings.extend(emb)

embeddings = np.array(embeddings).astype("float32")

# ========= STEP 5: FAISS =========

print("Building FAISS index...")

dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embeddings)

faiss.write_index(index, FAISS_INDEX_PATH)

# ========= STEP 6: SAVE METADATA =========

with open(ID_MAP_PATH, "w") as f:
    json.dump(cleaned, f, indent=2)  # keep compact for speed

print("Done")