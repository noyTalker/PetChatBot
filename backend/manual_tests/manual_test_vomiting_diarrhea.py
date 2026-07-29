import sys #הקאות/שלשולים   
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from inference.model_service import load_model, predict
from feature_engineering.symptom_mapper import map_answers_to_symptoms
from feature_engineering.alltext_builder import build_alltext

answers = {
    # Opening questions
    "animal_type":    "Dog",
    "breed":          "Labrador Retriever",
    "sex":            "Male",
    "age":            5.0,
    "weight_kg":      25.0,
    "main_complaint": "vomiting_diarrhea",

    # Red flags
    "breathing_now":                False,
    "collapse_unresponsive":        False,
    "seizures_now":                 False,
    "severe_bleeding_or_poisoning": False,
    "cannot_stand_or_walk":         False,

    # Path questions (vomiting_diarrhea)
    "vomiting":                   True,
    "vomiting_times":             "twice",
    "blood_in_vomit":             False,
    "diarrhea":                   True,
    "blood_in_stool":             False,
    "drinking":                   "normal",
    "lethargy":                   False,
    "swollen_or_painful_abdomen": False,
    "constipation":               False,
    "weight_loss_recent":         False,
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

