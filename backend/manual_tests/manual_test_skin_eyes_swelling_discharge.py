import sys #עור / עיניים / נפיחות / הפרשות  
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from inference.model_service import load_model, predict
from feature_engineering.symptom_mapper import map_answers_to_symptoms
from feature_engineering.alltext_builder import build_alltext

answers = {
    # Opening questions
    "animal_type":    "Cat",
    "breed":          "Siamese",
    "sex":            "Female",
    "age":            3.0,
    "weight_kg":      3.5,
    "main_complaint": "skin_eyes_swelling_discharge",

    # Red flags
    "breathing_now":                False,
    "collapse_unresponsive":        False,
    "seizures_now":                 False,
    "severe_bleeding_or_poisoning": False,
    "cannot_stand_or_walk":         False,

    # Path questions (skin_eyes_swelling_discharge)
    "swelling":                        True,
    "swelling_location":               "face",
    "eye_or_nose_discharge":           True,
    "red_eye_closed_eye_vision_problem": True,
    "skin_wound_redness_hair_loss":    True,
    "unusual_scratching_or_licking":   True,
    "scratching_location":             "eyes",
    "pain_in_area":                    True,
}

load_model()
symptoms = map_answers_to_symptoms(answers)
symptom_text = build_alltext(symptoms, metadata={})

print("Symptoms:", symptoms)
print("AllText:", symptom_text)

result = predict(
    symptom_text=symptom_text,
    breed=answers["breed"],
    animal_type=answers["animal_type"],
    age=answers["age"],
    weight_kg=answers["weight_kg"],
    answers=answers,
)

print("Result:", result)
