import joblib
import pandas as pd
import re
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "vet_triage_xgb_pipeline.pkl"

pipeline = None


def load_model():
    global pipeline
    pipeline = joblib.load(MODEL_PATH)


LABEL_MAP = {1: "Emergency", 0: "Not Emergency"}


_RED_FLAG_SYMPTOMS = (
    "breathing difficulty",
    "labored breathing",
    "collapse",
    "unresponsive",
    "sudden collapse",
    "loss of consciousness",
    "cannot stand",
    "seizure",
    "convulsions",
    "repeated seizures",
    "severe bleeding",
)


_KNOWN_SYMPTOM_TOKENS = [
    "open-mouth breathing",
    "loss of consciousness",
    "abnormal breath sounds",
    "repeated seizures",
    "repeated vomiting",
    "frequent vomiting",
    "blood in vomit",
    "bloody diarrhea",
    "not drinking",
    "excessive drinking",
    "abdominal pain",
    "swollen abdomen",
    "loss of appetite",
    "reduced appetite",
    "straining to urinate",
    "blood in urine",
    "eye discharge",
    "eye problem",
    "skin lesion",
    "blue gums",
    "pale gums",
    "breathing difficulty",
    "labored breathing",
    "sudden collapse",
    "severe bleeding",
    "cannot stand",
    "cannot walk",
    "non-weight bearing",
    "balance loss",
    "head tilt",
    "first seizure",
    "seizure",
    "convulsions",
    "bleeding",
    "coughing",
    "sneezing",
    "nasal discharge",
    "vomiting",
    "diarrhea",
    "lethargy",
    "weakness",
    "collapse",
    "tremor",
    "drooling",
    "fever",
    "high fever",
    "lameness",
    "pain",
    "trauma",
    "wound",
    "swelling",
    "constipation",
    "weight loss",
    "not urinating",
    "scratching",
]


_LOW_RISK_GI_CORE = (
    "vomiting",
    "repeated vomiting",
    "frequent vomiting",
    "diarrhea",
)

_HIGH_RISK_GI_SIGNS = (
    "blood in vomit",
    "bloody diarrhea",
    "not drinking",
    "excessive drinking",
    "lethargy",
    "abdominal pain",
    "swollen abdomen",
    "constipation",
    "weight loss",
)

_NON_GI_SIGNS = (
    "breathing difficulty",
    "labored breathing",
    "open-mouth breathing",
    "blue gums",
    "pale gums",
    "abnormal breath sounds",
    "coughing",
    "sneezing",
    "nasal discharge",
    "collapse",
    "unresponsive",
    "loss of consciousness",
    "cannot stand",
    "seizure",
    "convulsions",
    "severe bleeding",
    "weakness",
    "tremor",
    "balance loss",
    "drooling",
    "fever",
    "pain",
    "lameness",
    "trauma",
    "wound",
    "cannot walk",
    "loss of appetite",
    "reduced appetite",
    "not urinating",
    "straining to urinate",
    "blood in urine",
    "swelling",
    "eye discharge",
    "eye problem",
    "skin lesion",
    "scratching",
    "head tilt",
    "first seizure",
)


def _is_low_risk_gi_case(symptom_text: str) -> bool:
    """
    Force Not Emergency for mild GI-only patterns.
    Examples this covers:
      - vomiting + diarrhea, vomiting twice, everything else normal
      - same pattern with fewer symptoms (e.g., vomiting only)
    """
    text = " ".join(symptom_text.lower().split())
    if not text:
        return False

    # Must include at least one GI core signal
    if not any(token in text for token in _LOW_RISK_GI_CORE):
        return False

    # Any explicit high-risk GI sign cancels the override
    if any(token in text for token in _HIGH_RISK_GI_SIGNS):
        return False

    # Any non-GI / systemic sign cancels the override
    if any(token in text for token in _NON_GI_SIGNS):
        return False

    return True


def _has_red_flag_symptom(symptom_text: str) -> bool:
    text = " ".join(symptom_text.lower().split())
    if not text:
        return False

    return any(token in text for token in _RED_FLAG_SYMPTOMS)


def _count_matched_symptoms(symptom_text: str) -> int:
    text = " ".join(symptom_text.lower().split())
    if not text:
        return 0

    matches = []
    cursor = 0
    for token in sorted(_KNOWN_SYMPTOM_TOKENS, key=len, reverse=True):
        pattern = re.compile(rf"\b{re.escape(token)}\b")
        match = pattern.search(text, cursor)
        while match:
            matches.append((match.start(), match.end(), token))
            match = pattern.search(text, match.end())

    matches.sort(key=lambda item: (item[0], -(item[1] - item[0])))

    selected = []
    end_cursor = -1
    for start, end, token in matches:
        if start < end_cursor:
            continue
        selected.append(token)
        end_cursor = end

    return len(selected)


_RED_FLAG_ANSWER_KEYS = (
    "breathing_now",
    "collapse_unresponsive",
    "seizures_now",
    "severe_bleeding_or_poisoning",
    "cannot_stand_or_walk",
)


def _has_red_flag_answer(answers: dict) -> bool:
    """Return True if any red-flag question is answered True in the answers dict."""
    for key in _RED_FLAG_ANSWER_KEYS:
        val = answers.get(key)
        if val is None:
            continue
        if isinstance(val, bool) and val:
            return True
        if str(val).strip().lower() in ("yes", "true", "1"):
            return True
    return False


def predict(symptom_text: str, breed: str, animal_type: str, age: float, weight_kg: float, answers: dict = None) -> str:
    # 1. Red flag answers — direct user input, most reliable
    if answers is not None:
        if _has_red_flag_answer(answers):
            return "Emergency"
    else:
        # Fallback when answers dict is not available (e.g. manual tests)
        if _has_red_flag_symptom(symptom_text):
            return "Emergency"

    if _count_matched_symptoms(symptom_text) <= 1:
        return "Not Emergency"

    if _is_low_risk_gi_case(symptom_text):
        return "Not Emergency"

    # Normalise animal_type to title case to match training data ("cat" → "Cat")
    animal_type_norm = animal_type.strip().title()
    df = pd.DataFrame([{
        "AllText": symptom_text,
        "Breed": breed,
        "Animaltype": animal_type_norm,
        "Age": age,
        "Weight_kg": weight_kg,
    }])
    result = pipeline.predict(df)
    return LABEL_MAP.get(int(result[0]), str(result[0]))
