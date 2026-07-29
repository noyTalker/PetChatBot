"""
flow_engine.py

Core chatbot logic.

Responsibilities:
- Determine the next question based on current answers
- Detect when the conversation is complete
- Trigger feature engineering and model inference when done

Flow order:
  1. OPENING_QUESTIONS  (fixed, always asked in order)
  2. RED_FLAG_QUESTIONS (fixed, always asked after opening)
  3. PATHS[main_complaint] (dynamic, based on complaint answer)
  4. → model prediction
"""

from typing import Optional

from chatbot.flow_definitions import OPENING_QUESTIONS, RED_FLAG_QUESTIONS, PATHS
from chatbot.session_manager import create_session, get_session, update_session, inject_answer
from feature_engineering.symptom_mapper import map_answers_to_symptoms
from feature_engineering.alltext_builder import build_alltext
from inference.model_service import predict as model_predict


# ---------------------------------------------------------------------------
# Gender word replacements — applied when pet is Male
# (default question texts are written in feminine because "חיה" is feminine in Hebrew)
# ---------------------------------------------------------------------------

_MALE_REPLACEMENTS = [
    # multi-word phrases first (to avoid partial matches)
    ("בן/בת כמה", "בן כמה"),
    ("אינה מסוגלת", "אינו מסוגל"),
    ("אינה מגיבה", "אינו מגיב"),
    ("הרבה פחות פעילה מהרגיל", "הרבה פחות פעיל מהרגיל"),
    ("פחות פעילה מהרגיל", "פחות פעיל מהרגיל"),
    ("ולא פעילה", "ולא פעיל"),
    ("לא פעילה", "לא פעיל"),
    ("חוותה עוית", "חווה עוית"),
    ("עומדת והולכת", "עומד והולך"),
    ("מאבדת שיווי משקל או נופלת לצד אחד", "מאבד שיווי משקל או נופל לצד אחד"),
    ("מאבדת שיווי משקל או הולכת במעגלים", "מאבד שיווי משקל או הולך במעגלים"),
    ("מאבדת", "מאבד"),
    ("נופלת", "נופל"),
    ("נראית מבולבלת", "נראה מבולבל"),
    ("נראית כואבת", "נראה כואב"),
    ("נראית", "נראה"),
    ("מגרדת או מלקקת", "מגרד או מלקק"),
    ("מגרדת", "מגרד"),
    ("מלקקת", "מלקק"),
    ("מגיבה בכאב", "מגיב בכאב"),
    ("לא מגיבה", "לא מגיב"),
    # single verb forms
    ("משתעלת", "משתעל"),
    ("נושמת", "נושם"),
    ("מקיאה", "מקיא"),
    ("הקיאה", "הקיא"),
    ("רועדת", "רועד"),
    ("צולעת", "צולע"),
    ("נמנעת", "נמנע"),
    ("מגיבה", "מגיב"),
    ("מדממת", "מדמם"),
    ("מסוגלת", "מסוגל"),
    ("קרסה", "קרס"),
    ("ירדה", "ירד"),
    ("עייפה", "עייף"),
    ("פעילה", "פעיל"),
    ("חלשה", "חלש"),
    ("כואבת", "כואב"),
    ("הולכת", "הולך"),
    ("עומדת", "עומד"),
    ("אוכלת", "אוכל"),
    ("עשתה", "עשה"),
    ("מרירה", "מריר"),
    ("מבולבלת", "מבולבל"),
]

_FEMALE_REPLACEMENTS = [
    ("בן/בת כמה", "בת כמה"),
]


# ---------------------------------------------------------------------------
# Internal: compute the next unanswered question
# ---------------------------------------------------------------------------

def _personalize(q: dict, answers: dict) -> dict:
    """
    Personalise the question text using the pet name and gender.
    - Replaces "החיה שלך" with the pet's name.
    - Applies masculine/feminine Hebrew verb forms based on sex answer.
    """
    pet_name = str(answers.get("pet_name", "")).strip()
    sex = str(answers.get("sex", "")).strip()

    text = q["text"]
    has_pet_ref = "החיה שלך" in text

    # Substitute pet name
    if pet_name:
        text = text.replace("החיה שלך", pet_name)

    # Apply gender-aware replacements only for sentences that reference the pet
    if has_pet_ref:
        if sex == "Male":
            for old, new in _MALE_REPLACEMENTS:
                text = text.replace(old, new)
        elif sex == "Female":
            for old, new in _FEMALE_REPLACEMENTS:
                text = text.replace(old, new)
        else:
            # Unknown — leave בן/בת כמה as-is (already neutral)
            pass

    if text == q["text"]:
        return q
    return {**q, "text": text}


def _get_next_question(answers: dict) -> Optional[dict]:
    """
    Scan the question sequence in order and return the first unanswered one.
    Returns None when all questions have been answered.
    """
    # Phase 1: opening
    for q in OPENING_QUESTIONS:
        if q["id"] not in answers:
            # Resolve dynamic breed options based on animal_type
            if q["id"] == "breed" and "options_by_animal" in q:
                animal = str(answers.get("animal_type", ""))
                opts = q["options_by_animal"].get(animal)
                if opts:
                    q = {**q, "options": opts, "type": "choice"}
                else:
                    # Other animal — free text
                    q = {**q, "type": "text", "options": None}
            return _personalize(q, answers)

    # Phase 2: red flags
    for q in RED_FLAG_QUESTIONS:
        if q["id"] not in answers:
            return _personalize(q, answers)

    # Phase 3: dynamic path
    complaint = str(answers.get("main_complaint", "other")).strip().lower()
    path = PATHS.get(complaint, PATHS["other"])
    for q in path:
        if q["id"] not in answers:
            return _personalize(q, answers)

    return None  # all questions answered


# ---------------------------------------------------------------------------
# Internal: run prediction pipeline
# ---------------------------------------------------------------------------

def _build_result(answers: dict) -> dict:
    """
    Called when all questions are answered.
    Runs the full feature engineering → model pipeline and returns the result.
    If no specific symptoms were flagged (all path answers were negative),
    return "Not Emergency" immediately without calling the model.
    """
    age = float(answers.get("age", 0))
    weight_kg = float(answers.get("weight_kg", 0))

    symptoms = map_answers_to_symptoms(answers)
    metadata = {
        "medical_history": str(answers.get("medical_history", "")),
    }
    symptom_text = build_alltext(symptoms, metadata)

    # If the symptom text is empty or contains no real clinical tokens,
    # there is nothing to predict — return Not Emergency directly.
    if not symptom_text.strip():
        return {
            "done": True,
            "prediction": "Not Emergency",
            "alltext": symptom_text,
            "answers": answers,
        }

    breed = str(answers.get("breed", ""))
    animal_type = str(answers.get("animal_type", ""))
    prediction = model_predict(
        symptom_text=symptom_text,
        breed=breed,
        animal_type=animal_type,
        age=age,
        weight_kg=weight_kg,
        answers=answers,
    )

    return {
        "done": True,
        "prediction": prediction,
        "alltext": symptom_text,
        "answers": answers,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def start_conversation() -> dict:
    """
    Start a new conversation.

    Returns:
        {
            "session_id": "...",
            "question": { id, text, type, options }
        }
    """
    first_question = OPENING_QUESTIONS[0]
    session_id = create_session(first_question_id=first_question["id"])
    return {
        "session_id": session_id,
        "question": first_question,
    }


def answer_question(session_id: str, answer) -> dict:
    """
    Submit an answer for the current question.

    Args:
        session_id: active session id
        answer:     the user's answer (bool, str, float, int)

    Returns one of:

    Next question:
        {
            "done": False,
            "question": { id, text, type, options }
        }

    Final result:
        {
            "done": True,
            "prediction": "Emergency" | "Not Emergency",
            "alltext": "...",
            "answers": { ... }
        }

    Raises:
        KeyError if session_id is not found.
    """
    session = get_session(session_id)
    if session is None:
        raise KeyError(f"Session not found: {session_id}")

    current_q_id = session["current_question_id"]
    if current_q_id is None:
        # Conversation already completed — return stored result
        raise ValueError("This conversation has already ended.")

    # Temporarily store the answer to compute next question
    answers_snapshot = {**session["answers"], current_q_id: answer}

    # Skip logic: auto-inject minimum answers for dependent follow-up questions
    auto_skips = {}
    if current_q_id == "vomiting" and answer is False:
        auto_skips["vomiting_times"] = "once"
        auto_skips["blood_in_vomit"] = False
        answers_snapshot["vomiting_times"] = "once"
        answers_snapshot["blood_in_vomit"] = False
    if current_q_id == "fever" and answer is False:
        auto_skips["fever_range"] = "mild"
        answers_snapshot["fever_range"] = "mild"

    next_q = _get_next_question(answers_snapshot)
    next_q_id = next_q["id"] if next_q else None

    # Persist the real answer
    update_session(
        session_id=session_id,
        question_id=current_q_id,
        answer=answer,
        next_question_id=next_q_id,
    )

    # Persist silently skipped answers
    for skipped_id, skipped_val in auto_skips.items():
        inject_answer(session_id, skipped_id, skipped_val)

    if next_q:
        return {"done": False, "question": next_q}

    # All questions answered — run the model
    final_answers = get_session(session_id)["answers"]
    return _build_result(final_answers)
