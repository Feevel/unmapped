from vector_store import search_esco

def extract_skills_with_ids(user_input: str):
    result = search_esco(user_input)

    return [
        {
            "id": skill["id"],
            "name": skill["name"]
        }
        for skill in result["results"]
    ]
