from occupation_to_skills import get_skills_for_occupation

def extract_skills_from_occupation(occupation: str):
    result = get_skills_for_occupation(occupation)

    return [
        {
            "id": skill["id"],
            "name": skill["name"]
        }
        for skill in result
    ]

print(extract_skills_from_occupation("kitchen assistant"))