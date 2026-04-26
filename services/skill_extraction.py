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

print(extract_skills_with_ids("""
    I have repaired phones for 5 years. I replace screens, fix charging ports,
    install apps, talk to customers, buy spare parts, and manage payments.
    I also learned basic coding from YouTube.
    """))