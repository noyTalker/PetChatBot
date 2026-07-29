import sys #כאב/צימאון/קושי בתנועה
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from inference.model_service import load_model, predict
from feature_engineering.symptom_mapper import map_answers_to_symptoms
from feature_engineering.alltext_builder import build_alltext

answers = {
    # Opening questions
    "animal_type":    "Dog",
    "breed":          "German Shepherd",
    "sex":            "Male",
    "age":            5.0,
    "weight_kg":      35.0,
    "main_complaint": "pain_limping_mobility",

    # Red flags
    "breathing_now":                False,
    "collapse_unresponsive":        False,
    "seizures_now":                 False,
    "severe_bleeding_or_poisoning": False,
    "cannot_stand_or_walk":         False,

    # Path questions (pain_limping_mobility)
    "limping":                      True,
    "avoids_weight_on_leg":         True,
    "pain_on_touch":                False,
    "swelling":                     True,
    "swelling_location":            "leg",
    "trauma_or_fall":               False,
    "walking_ability":              "lamer",
    "stiffness_or_difficulty_rising": False,
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

