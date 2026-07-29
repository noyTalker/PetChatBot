"""
symptom_mapper.py

Converts structured chatbot answers into a list of canonical symptom strings
that match the vocabulary style used during model training.

Flow:
  1. Red flags (asked for every pet) — always mapped first
  2. Main complaint contributes its own symptom token
  3. Dynamic path based on main_complaint value
"""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _flag(answers: dict, key: str) -> bool:
    """Return True if the answer for key is truthy (True, 'yes', 'true')."""
    val = answers.get(key)
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("yes", "true", "1")


def _val(answers: dict, key: str) -> str:
    """Return the lowercased string value for a key, or ''."""
    val = answers.get(key)
    if val is None:
        return ""
    return str(val).strip().lower()


# ---------------------------------------------------------------------------
# Section mappers
# ---------------------------------------------------------------------------

def _map_red_flags(answers: dict, symptoms: list) -> None:
    if _flag(answers, "breathing_now"):
        symptoms.append("breathing difficulty")
        symptoms.append("labored breathing")
    if _flag(answers, "collapse_unresponsive"):
        symptoms.append("collapse")
        symptoms.append("unresponsive")
        symptoms.append("sudden collapse")
        symptoms.append("loss of consciousness")
        symptoms.append("cannot stand")
    if _flag(answers, "seizures_now"):
        symptoms.append("seizure")
        symptoms.append("convulsions")
        symptoms.append("repeated seizures")
    if _flag(answers, "severe_bleeding_or_poisoning"):
        symptoms.append("severe bleeding")
    if _flag(answers, "cannot_stand_or_walk"):
        symptoms.append("cannot stand")


def _map_main_complaint_token(answers: dict, symptoms: list) -> None:
    """Add the main complaint token only if at least one path symptom is already present."""
    COMPLAINT_TOKENS = {
        "vomiting_diarrhea":           "vomiting",
        "cough_sneeze":                "coughing",
        "weakness_apathy_collapse":    "weakness",
        "pain_limping_mobility":       "pain",
        "bleeding_trauma":             "bleeding",
        "appetite_drinking":           "loss of appetite",
        "skin_eyes_swelling_discharge":"skin lesion",
        "seizure_neurological":        "seizure",
    }
    complaint = _val(answers, "main_complaint")
    token = COMPLAINT_TOKENS.get(complaint)
    # Only add the complaint token if at least one specific symptom was already flagged
    if token and token not in symptoms and len(symptoms) > 0:
        symptoms.append(token)


# --- Path 1: breathing / cough ---
def _map_breathing_cough(answers: dict, symptoms: list) -> None:
    if _flag(answers, "cough"):
        symptoms.append("coughing")
    if _flag(answers, "sneezing_or_nasal_discharge"):
        symptoms.append("sneezing")
        symptoms.append("nasal discharge")
    if _flag(answers, "fast_or_labored_breathing"):
        symptoms.append("labored breathing")
    if _flag(answers, "open_mouth_breathing"):
        symptoms.append("open-mouth breathing")
    gums = _val(answers, "gum_color")
    if gums in ("blue", "purple"):
        symptoms.append("blue gums")
    elif gums in ("pale", "white"):
        symptoms.append("pale gums")
    if _flag(answers, "abnormal_breath_sounds"):
        symptoms.append("abnormal breath sounds")


# --- Path 2: vomiting / diarrhea ---
def _map_vomiting_diarrhea(answers: dict, symptoms: list) -> None:
    if _flag(answers, "vomiting"):
        symptoms.append("vomiting")
        times = _val(answers, "vomiting_times")
        if times in ("more_than_3", "frequent"):
            symptoms.append("frequent vomiting")
        elif times in ("2_to_3", "twice", "repeated"):
            symptoms.append("repeated vomiting")
    if _flag(answers, "blood_in_vomit"):
        symptoms.append("blood in vomit")
    if _flag(answers, "diarrhea"):
        symptoms.append("diarrhea")
    if _flag(answers, "blood_in_stool"):
        symptoms.append("bloody diarrhea")
    drinking = _val(answers, "drinking")
    if drinking in ("not", "no", "none"):
        symptoms.append("not drinking")
    elif drinking in ("excessive", "increased"):
        symptoms.append("excessive drinking")
    if _flag(answers, "lethargy"):
        symptoms.append("lethargy")
    if _flag(answers, "swollen_or_painful_abdomen"):
        symptoms.append("abdominal pain")
        symptoms.append("swollen abdomen")
    if _flag(answers, "constipation"):
        symptoms.append("constipation")
    if _flag(answers, "weight_loss_recent"):
        symptoms.append("weight loss")


# --- Path 3: weakness / apathy / collapse ---
def _map_weakness_collapse(answers: dict, symptoms: list) -> None:
    if _flag(answers, "low_activity"):
        symptoms.append("lethargy")
    standing = _val(answers, "standing_and_walking")
    if standing in ("no", "cannot"):
        symptoms.append("cannot stand")
    elif standing in ("difficulty", "barely"):
        symptoms.append("weakness")
    if _flag(answers, "sudden_collapse"):
        symptoms.append("collapse")
    eating = _val(answers, "eating")
    if eating in ("not", "no", "none"):
        symptoms.append("loss of appetite")
    elif eating in ("reduced", "less"):
        symptoms.append("reduced appetite")
    drinking = _val(answers, "drinking")
    if drinking in ("not", "no", "none"):
        symptoms.append("not drinking")
    if _flag(answers, "tremors"):
        symptoms.append("tremor")
    if _flag(answers, "balance_loss"):
        symptoms.append("balance loss")
    if _flag(answers, "drooling"):
        symptoms.append("drooling")
    fever = _val(answers, "fever")
    if fever in ("yes", "true", "1"):
        symptoms.append("fever")
        fever_range = _val(answers, "fever_range")
        if fever_range in ("high", "very_high", "above_40"):
            symptoms.append("high fever")


# --- Path 4: pain / limping / mobility ---
def _map_pain_mobility(answers: dict, symptoms: list) -> None:
    if _flag(answers, "limping"):
        symptoms.append("lameness")
    if _flag(answers, "avoids_weight_on_leg"):
        symptoms.append("non-weight bearing")
    if _flag(answers, "pain_on_touch"):
        symptoms.append("pain")
    if _flag(answers, "swelling"):
        symptoms.append("swelling")
        loc = _val(answers, "swelling_location")
        if loc:
            symptoms.append(f"swelling {loc}")
    if _flag(answers, "trauma_or_fall"):
        symptoms.append("trauma")
    walking = _val(answers, "walking_ability")
    if walking in ("cannot", "no"):
        symptoms.append("cannot walk")
    elif walking in ("difficulty", "limping"):
        symptoms.append("lameness")
    if _flag(answers, "stiffness_or_difficulty_rising"):
        symptoms.append("stiffness")


# --- Path 5: bleeding / trauma ---
def _map_bleeding_trauma(answers: dict, symptoms: list) -> None:
    if _flag(answers, "bleeding_now"):
        symptoms.append("bleeding")
    if _flag(answers, "bleeding_not_stopping"):
        symptoms.append("severe bleeding")
    if _flag(answers, "accident_fall_hit"):
        symptoms.append("trauma")
    if _flag(answers, "open_wound"):
        symptoms.append("wound")
    walking = _val(answers, "walking_after_trauma")
    if walking in ("no", "cannot"):
        symptoms.append("cannot walk")


# --- Path 6: appetite / drinking ---
def _map_appetite_drinking(answers: dict, symptoms: list) -> None:
    eating = _val(answers, "eating")
    if eating in ("not", "no", "none"):
        symptoms.append("loss of appetite")
    elif eating in ("reduced", "less"):
        symptoms.append("reduced appetite")
    drinking = _val(answers, "drinking")
    if drinking in ("not", "no", "none"):
        symptoms.append("not drinking")
    elif drinking in ("excessive", "increased"):
        symptoms.append("excessive drinking")
    if _flag(answers, "vomiting"):
        symptoms.append("vomiting")
    if _flag(answers, "diarrhea"):
        symptoms.append("diarrhea")
    if _flag(answers, "weak_or_less_active"):
        symptoms.append("lethargy")
    urination = _val(answers, "urination_change")
    if urination in ("not", "none", "no"):
        symptoms.append("not urinating")
    elif urination in ("straining",):
        symptoms.append("straining to urinate")
    elif urination in ("blood",):
        symptoms.append("blood in urine")
    if _flag(answers, "weight_loss_recent"):
        symptoms.append("weight loss")


# --- Path 7: skin / eyes / swelling / discharge ---
def _map_skin_eyes(answers: dict, symptoms: list) -> None:
    if _flag(answers, "swelling"):
        symptoms.append("swelling")
        loc = _val(answers, "swelling_location")
        if loc:
            symptoms.append(f"swelling {loc}")
    if _flag(answers, "eye_or_nose_discharge"):
        symptoms.append("eye discharge")
    if _flag(answers, "red_eye_closed_eye_vision_problem"):
        symptoms.append("eye problem")
    if _flag(answers, "skin_wound_redness_hair_loss"):
        symptoms.append("skin lesion")
    if _flag(answers, "unusual_scratching_or_licking"):
        symptoms.append("scratching")
        loc = _val(answers, "scratching_location")
        if loc:
            symptoms.append(f"scratching {loc}")
    if _flag(answers, "pain_in_area"):
        symptoms.append("pain")


# --- Path 8: seizure / neurological ---
def _map_seizure_neurological(answers: dict, symptoms: list) -> None:
    if _flag(answers, "seizures"):
        symptoms.append("seizure")
        symptoms.append("convulsions")
        if not _flag(answers, "first_time_event"):
            symptoms.append("repeated seizures")
    if _flag(answers, "balance_loss"):
        symptoms.append("balance loss")
    if _flag(answers, "tremor_abnormal"):
        symptoms.append("tremor")
    if _flag(answers, "confused_or_unresponsive"):
        symptoms.append("unresponsive")
    if _flag(answers, "head_tilt"):
        symptoms.append("head tilt")
    if _flag(answers, "first_time_event"):
        symptoms.append("first seizure")


# --- Path 9: other / fallback ---
def _map_other(answers: dict, symptoms: list) -> None:
    """
    'other' routes to the relevant sub-path based on fallback_symptom_category.
    """
    PATH_DISPATCH = {
        "breathing": _map_breathing_cough,
        "cough":     _map_breathing_cough,
        "vomiting":  _map_vomiting_diarrhea,
        "diarrhea":  _map_vomiting_diarrhea,
        "weakness":  _map_weakness_collapse,
        "pain":      _map_pain_mobility,
        "bleeding":  _map_bleeding_trauma,
        "appetite":  _map_appetite_drinking,
        "skin":      _map_skin_eyes,
        "seizure":   _map_seizure_neurological,
        "neuro":     _map_seizure_neurological,
    }
    fallback = _val(answers, "fallback_symptom_category")
    handler = PATH_DISPATCH.get(fallback)
    if handler:
        handler(answers, symptoms)


# ---------------------------------------------------------------------------
# Main dispatcher
# ---------------------------------------------------------------------------

_PATH_DISPATCH = {
    "cough_sneeze":                _map_breathing_cough,
    "vomiting_diarrhea":           _map_vomiting_diarrhea,
    "weakness_apathy_collapse":    _map_weakness_collapse,
    "pain_limping_mobility":       _map_pain_mobility,
    "bleeding_trauma":             _map_bleeding_trauma,
    "appetite_drinking":           _map_appetite_drinking,
    "skin_eyes_swelling_discharge":_map_skin_eyes,
    "seizure_neurological":        _map_seizure_neurological,
    "other":                       _map_other,
}


def map_answers_to_symptoms(answers: dict) -> list:
    """
    Converts a structured answers dict into a list of canonical symptom strings.

    Order:
      1. Red flags (always)
      2. Main complaint token
      3. Dynamic path based on main_complaint
    """
    symptoms: list = []

    _map_red_flags(answers, symptoms)
    _map_main_complaint_token(answers, symptoms)

    complaint = _val(answers, "main_complaint")
    handler = _PATH_DISPATCH.get(complaint)
    if handler:
        handler(answers, symptoms)

    # Deduplicate while preserving order
    seen = set()
    unique: list = []
    for s in symptoms:
        if s not in seen:
            seen.add(s)
            unique.append(s)

    return unique

