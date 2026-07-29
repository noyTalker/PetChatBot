import sys # חולשה / אדישות / קריסה
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from inference.model_service import load_model, predict
from feature_engineering.symptom_mapper import map_answers_to_symptoms
from feature_engineering.alltext_builder import build_alltext

answers = {
    # Opening questions
    "animal_type":    "Dog",
    "breed":          "Golden Retriever",
    "sex":            "Female",
    "age":            7.0,
    "weight_kg":      30.0,
    "main_complaint": "weakness_apathy_collapse",

    # Red flags
    "breathing_now":                False,
    "collapse_unresponsive":        False,
    "seizures_now":                 False,
    "severe_bleeding_or_poisoning": False,
    "cannot_stand_or_walk":         False,

    # Path questions (weakness_apathy_collapse) - two mild symptoms only
    "low_activity":         True,
    "standing_and_walking": "normal",
    "sudden_collapse":      True,
    "eating":               "reduced",
    "drinking":             "normal",
    "tremors":              False,
    "balance_loss":         False,
    "drooling":             False,
    "fever":                False,
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


