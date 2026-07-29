"""
alltext_builder.py

Assembles the AllText string from symptoms and medical history ONLY.
Breed and animal type are passed as separate features to the model pipeline.
"""


def build_alltext(symptoms: list, metadata: dict) -> str:
    """
    Combines symptom list and medical history into a single text string.
    Breed and animal type are intentionally excluded here — they are
    passed as separate categorical features in model_service.predict().

    Args:
        symptoms: list of canonical symptom strings from symptom_mapper
        metadata: dict with optional keys:
            - medical_history (str): optional free text

    Returns:
        A single space-joined symptoms + medical history string.
    """
    parts = list(symptoms)

    medical_history = metadata.get("medical_history", "").strip()
    if medical_history:
        parts.append(medical_history)

    return " ".join(parts)
