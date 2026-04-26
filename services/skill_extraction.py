from services.vector_store import search_esco

def extract_skills_with_ids(user_input: str):
    result = search_esco(user_input)

    return [
        {
            "id": skill["id"],
            "name": skill["name"],
            "confidence": skill.get("confidence"),
            "source_query": skill.get("source_query"),
            "explanation": skill.get("explanation"),
        }
        for skill in result["results"]
    ]
