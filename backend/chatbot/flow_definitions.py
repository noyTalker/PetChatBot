"""
flow_definitions.py

Defines all chatbot questions as plain Python data structures.

Each question dict has:
  id      - key used to store the answer (must match symptom_mapper keys)
  text    - question shown to the user
  type    - "choice" | "boolean" | "numeric" | "text"
  options - list of valid string values (for choice), None otherwise
"""

# ---------------------------------------------------------------------------
# Opening questions — asked for every pet, in this order
# ---------------------------------------------------------------------------

OPENING_QUESTIONS = [
    {
        "id": "animal_type",
        "text": "איזה סוג חיה יש לך?",
        "type": "choice",
        "options": ["Dog", "Cat"],
    },
    {
        "id": "pet_name",
        "text": "מה שמה/שמו של החיה שלך?",
        "type": "text",
        "options": None,
    },
    {
        "id": "breed",
        "text": "מה הגזע?",
        "type": "choice",
        "options": None,  # resolved dynamically based on animal_type
        "options_by_animal": {
            "Dog": [
                "Beagle",
                "Boxer",
                "Bulldog",
                "German Shepherd",
                "Golden Retriever",
                "Labrador Retriever",
                "Mixed Breed",
                "Poodle",
                "Rottweiler",
                "Yorkshire Terrier",
            ],
            "Cat": [
                "Bengal",
                "British Shorthair",
                "Maine Coon",
                "Mixed Breed",
                "Persian",
                "Ragdoll",
                "Scottish Fold",
                "Siamese",
                "Sphynx",
            ],
        },
    },
    {
        "id": "sex",
        "text": "מה המין של החיה שלך?",
        "type": "choice",
        "options": ["Male", "Female"],
    },
    {
        "id": "age",
        "text": "בן/בת כמה החיה שלך? (בשנים)",
        "type": "numeric",
        "options": None,
    },
    {
        "id": "weight_kg",
        "text": "מה משקל החיה שלך? (בקג)",
        "type": "numeric",
        "options": None,
    },
    {
        "id": "main_complaint",
        "text": "מה הסיבה העיקרית שבגללה פנית לעזרה היום?",
        "type": "choice",
        "options": [
            "cough_sneeze",
            "vomiting_diarrhea",
            "weakness_apathy_collapse",
            "pain_limping_mobility",
            "bleeding_trauma",
            "appetite_drinking",
            "skin_eyes_swelling_discharge",
            "seizure_neurological",
        ],
    },
]

# ---------------------------------------------------------------------------
# Red flag questions — asked for every pet, after opening
# ---------------------------------------------------------------------------

RED_FLAG_QUESTIONS = [
    {
        "id": "breathing_now",
        "text": "האם החיה שלך מתקשה מאוד לנשום כרגע?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "collapse_unresponsive",
        "text": "האם החיה שלך קרסה או אינה מגיבה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "seizures_now",
        "text": "האם החיה שלך חווה פרכוס כרגע?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "severe_bleeding_or_poisoning",
        "text": "האם יש דימום חמור שאינו נעצר, או חשד להרעלה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "cannot_stand_or_walk",
        "text": "האם החיה שלך אינה מסוגלת לעמוד או ללכת כלל?",
        "type": "boolean",
        "options": None,
    },
]

# ---------------------------------------------------------------------------
# Dynamic paths — one list per main_complaint value
# (keys match symptom_mapper expectations exactly)
# ---------------------------------------------------------------------------

_BREATHING_COUGH_PATH = [
    {
        "id": "cough",
        "text": "האם החיה שלך משתעלת?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "sneezing_or_nasal_discharge",
        "text": "האם יש התעטשות או הפרשות מהאף?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "fast_or_labored_breathing",
        "text": "האם הנשימה מהירה או כבדה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "open_mouth_breathing",
        "text": "האם החיה שלך נושמת בפה פתוח?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "gum_color",
        "text": "איזה צבע יש לחניכיים?",
        "type": "choice",
        "options": ["normal", "pale", "white", "blue", "yellow"],
    },
    {
        "id": "abnormal_breath_sounds",
        "text": "האם נשמעים קולות נשימה חריגים (שריקות, רחשים)?",
        "type": "boolean",
        "options": None,
    },
]

_VOMITING_DIARRHEA_PATH = [
    {
        "id": "vomiting",
        "text": "האם החיה שלך מקיאה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "vomiting_times",
        "text": "כמה פעמים הקיאה החיה שלך?",
        "type": "choice",
        "options": ["once", "twice", "more_than_3"],
    },
    {
        "id": "blood_in_vomit",
        "text": "האם יש דם בהקאה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "diarrhea",
        "text": "האם יש לחיה שלך שלשול?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "blood_in_stool",
        "text": "האם יש דם בצואה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "drinking",
        "text": "כיצד החיה שלך שותה?",
        "type": "choice",
        "options": ["normal", "reduced", "not"],
    },
    {
        "id": "lethargy",
        "text": "האם החיה שלך עייפה ולא פעילה באופן חריג?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "swollen_or_painful_abdomen",
        "text": "האם הבטן נראית נפוחה או כואבת?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "constipation",
        "text": "האם החיה שלך לא עשתה צרכים כבר יותר מ-48 שעות?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "weight_loss_recent",
        "text": "האם החיה שלך ירדה במשקל לאחרונה?",
        "type": "boolean",
        "options": None,
    },
]

_WEAKNESS_COLLAPSE_PATH = [
    {
        "id": "low_activity",
        "text": "האם החיה שלך הרבה פחות פעילה מהרגיל?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "standing_and_walking",
        "text": "כיצד החיה שלך עומדת והולכת?",
        "type": "choice",
        "options": ["normal", "difficulty", "barely", "cannot"],
    },
    {
        "id": "sudden_collapse",
        "text": "האם החיה שלך קרסה פתאום?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "eating",
        "text": "כיצד החיה שלך אוכלת?",
        "type": "choice",
        "options": ["normal", "reduced", "not"],
    },
    {
        "id": "drinking",
        "text": "כיצד החיה שלך שותה?",
        "type": "choice",
        "options": ["normal", "reduced", "not"],
    },
    {
        "id": "tremors",
        "text": "האם החיה שלך רועדת?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "balance_loss",
        "text": "האם החיה שלך מאבדת שיווי משקל או הולכת במעגלים?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "drooling",
        "text": "האם החיה שלך מרירה באופן מוגזם?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "fever",
        "text": "האם נראה שיש לחיה שלך חום?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "fever_range",
        "text": "עד כמה החום מרגיש חמור?",
        "type": "choice",
        "options": ["mild", "high", "very_high"],
    },
]

_PAIN_MOBILITY_PATH = [
    {
        "id": "limping",
        "text": "האם החיה שלך צולעת?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "avoids_weight_on_leg",
        "text": "האם החיה שלך נמנעת מלדרוך על רגל מסוימת?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "pain_on_touch",
        "text": "האם החיה שלך מגיבה בכאב כשנוגעים בה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "swelling",
        "text": "האם יש נפיחות גלויה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "swelling_location",
        "text": "היכן ממוקמת הנפיחות?",
        "type": "choice",
        "options": ["leg", "abdomen", "face", "neck", "other"],
    },
    {
        "id": "trauma_or_fall",
        "text": "האם הייתה פגיעה, נפילה או תאונה לאחרונה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "walking_ability",
        "text": "מה יכולת ההליכה של החיה שלך?",
        "type": "choice",
        "options": ["normal", "limping", "difficulty", "cannot"],
    },
    {
        "id": "stiffness_or_difficulty_rising",
        "text": "האם החיה שלך נוקשה או מתקשה לקום?",
        "type": "boolean",
        "options": None,
    },
]

_BLEEDING_TRAUMA_PATH = [
    {
        "id": "bleeding_now",
        "text": "האם החיה שלך מדממת כרגע?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "bleeding_not_stopping",
        "text": "האם הדימום אינו נעצר גם לאחר לחץ?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "accident_fall_hit",
        "text": "האם הייתה תאונה, נפילה או מכה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "open_wound",
        "text": "האם יש פצע פתוח גלוי?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "walking_after_trauma",
        "text": "האם החיה שלך מסוגלת ללכת לאחר הטראומה?",
        "type": "choice",
        "options": ["yes", "difficulty", "no"],
    },
]

_APPETITE_DRINKING_PATH = [
    {
        "id": "eating",
        "text": "כיצד החיה שלך אוכלת?",
        "type": "choice",
        "options": ["normal", "reduced", "not"],
    },
    {
        "id": "drinking",
        "text": "כיצד החיה שלך שותה?",
        "type": "choice",
        "options": ["normal", "reduced", "not"],
    },
    {
        "id": "vomiting",
        "text": "האם החיה שלך מקיאה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "diarrhea",
        "text": "האם יש לחיה שלך שלשול?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "weak_or_less_active",
        "text": "האם החיה שלך חלשה או פחות פעילה מהרגיל?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "urination_change",
        "text": "האם חל שינוי בהטלת השתן?",
        "type": "choice",
        "options": ["normal", "not", "straining", "blood"],
    },
    {
        "id": "weight_loss_recent",
        "text": "האם החיה שלך ירדה במשקל לאחרונה?",
        "type": "boolean",
        "options": None,
    },
]

_SKIN_EYES_PATH = [
    {
        "id": "swelling",
        "text": "האם יש נפיחות גלויה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "swelling_location",
        "text": "היכן ממוקמת הנפיחות?",
        "type": "choice",
        "options": ["leg", "abdomen", "face", "neck", "other"],
    },
    {
        "id": "eye_or_nose_discharge",
        "text": "האם יש הפרשות מהעיניים או מהאף?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "red_eye_closed_eye_vision_problem",
        "text": "האם יש עין אדומה, עין עצומה, או בעיה נראית בראייה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "skin_wound_redness_hair_loss",
        "text": "האם יש פצע עורי, אדמומיות, או נשירת שיער?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "unusual_scratching_or_licking",
        "text": "האם החיה שלך מגרדת או מלקקת אזור מסוים באופן חריג?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "scratching_location",
        "text": "היכן הגירוד או הליקוק?",
        "type": "choice",
        "options": ["ears", "eyes", "skin", "paws", "other"],
    },
    {
        "id": "pain_in_area",
        "text": "האם החיה שלך נראית כואבת באזור הפגוע?",
        "type": "boolean",
        "options": None,
    },
]

_SEIZURE_NEURO_PATH = [
    {
        "id": "seizures",
        "text": "האם החיה שלך חוותה עוית (פרכוסים, רעידות בלתי נשלטות)?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "balance_loss",
        "text": "האם החיה שלך מאבדת שיווי משקל או נופלת לצד אחד?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "tremor_abnormal",
        "text": "האם יש רעידות או תנועות לא רצוניות חריגות?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "confused_or_unresponsive",
        "text": "האם החיה שלך נראית מבולבלת או לא מגיבה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "head_tilt",
        "text": "האם יש הטיית ראש מתמשכת?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "first_time_event",
        "text": "האם זו הפעם הראשונה שזה קורה?",
        "type": "boolean",
        "options": None,
    },
]

_OTHER_PATH = [
    {
        "id": "fallback_symptom_category",
        "text": "איזו קטגוריה מתארת הכי טוב את הבעיה העיקרית?",
        "type": "choice",
        "options": [
            "breathing", "cough", "vomiting", "diarrhea",
            "weakness", "pain", "bleeding", "appetite",
            "skin", "seizure", "neuro",
        ],
    },
    {
        "id": "lethargy",
        "text": "האם החיה שלך עייפה ולא פעילה באופן חריג?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "vomiting",
        "text": "האם החיה שלך מקיאה?",
        "type": "boolean",
        "options": None,
    },
    {
        "id": "drinking",
        "text": "כיצד החיה שלך שותה?",
        "type": "choice",
        "options": ["normal", "reduced", "not"],
    },
]

# ---------------------------------------------------------------------------
# Path dispatch — maps main_complaint value to its question list
# ---------------------------------------------------------------------------

PATHS = {
    "cough_sneeze":                 _BREATHING_COUGH_PATH,
    "vomiting_diarrhea":            _VOMITING_DIARRHEA_PATH,
    "weakness_apathy_collapse":     _WEAKNESS_COLLAPSE_PATH,
    "pain_limping_mobility":        _PAIN_MOBILITY_PATH,
    "bleeding_trauma":              _BLEEDING_TRAUMA_PATH,
    "appetite_drinking":            _APPETITE_DRINKING_PATH,
    "skin_eyes_swelling_discharge": _SKIN_EYES_PATH,
    "seizure_neurological":         _SEIZURE_NEURO_PATH,
    "other":                        _OTHER_PATH,
}
