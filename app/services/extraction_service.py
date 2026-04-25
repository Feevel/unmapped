def extract_skills_from_text(text: str):
    """
    Temporary simple skill extraction.
    Later this will be replaced with an LLM.
    """

    skills = []

    text = text.lower()

    if "repair" in text:
        skills.append("phone repair")

    if "customer" in text:
        skills.append("customer service")

    if "payment" in text:
        skills.append("cash handling")

    if "coding" in text:
        skills.append("basic programming")

    return skills