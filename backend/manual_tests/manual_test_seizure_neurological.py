import sys #פרכוסים / נוירולוגי 
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from inference.model_service import load_model, predict
from feature_engineering.symptom_mapper import map_answers_to_symptoms
from feature_engineering.alltext_builder import build_alltext

answers = {
    # Opening questions
    "animal_type":    "Dog",
    "breed":          "Beagle",
    "sex":            "Male",
    "age":            4.0,
    "weight_kg":      12.0,
    "main_complaint": "seizure_neurological",

    # Red flags
    "breathing_now":                False,
    "collapse_unresponsive":        False,
    "seizures_now":                 True,
    "severe_bleeding_or_poisoning": False,
    "cannot_stand_or_walk":         False,

    # Path questions (seizure_neurological)
    "seizures":               True,
    "balance_loss":           True,
    "tremor_abnormal":        True,
    "confused_or_unresponsive": True,
    "head_tilt":              False,
    "first_time_event":       True,
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

