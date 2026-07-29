import { useState } from "react";
import type { Question } from "../api/chatApi";

interface Props {
  question: Question;
  onAnswer: (answer: unknown, displayText: string) => void;
  disabled?: boolean;
}

/** Convert option codes to readable Hebrew labels */
const OPTION_LABELS: Record<string, string> = {
  // animal types
  Dog: "כלב",
  Cat: "חתול",
  // dog breeds
  Beagle: "ביגל",
  Boxer: "בוקסר",
  Bulldog: "בולדוג",
  "German Shepherd": "רועה גרמני",
  "Golden Retriever": "גולדן רטריבר",
  "Labrador Retriever": "לברדור רטריבר",
  "Mixed Breed": "כלאיים",
  Poodle: "פודל",
  Rottweiler: "רוטוויילר",
  "Yorkshire Terrier": "יורקשייר טרייר",
  // cat breeds
  Bengal: "בנגל",
  "British Shorthair": "בריטי שורטהייר",
  "Maine Coon": "מיין קון",
  Persian: "פרסי",
  Ragdoll: "רגדול",
  "Scottish Fold": "סקוטיש פולד",
  Siamese: "סיאמי",
  Sphynx: "ספינקס",
  // sex
  Male: "זכר",
  Female: "נקבה",
  // main complaint
  breathing_difficulty: "קושי בנשימה",
  cough_sneeze: "שיעול / התעטשות",
  vomiting_diarrhea: "הקאות / שלשול",
  weakness_apathy_collapse: "חולשה / אדישות / קריסה",
  pain_limping_mobility: "כאב / צליעה / תנועה",
  bleeding_trauma: "דימום / טראומה",
  appetite_drinking: "תיאבון / שתייה",
  skin_eyes_swelling_discharge: "עור / עיניים / נפיחות / הפרשות",
  seizure_neurological: "פרכוסים / נוירולוגי",
  other: "אחר",
  // gum color
  normal: "תקין",
  pale: "חיוור",
  white: "לבן",
  blue: "כחול",
  yellow: "צהוב",
  // vomiting times
  once: "פעם אחת",
  twice: "פעמיים",
  more_than_3: "יותר מ-3 פעמים",
  // drinking / eating
  reduced: "מופחת",
  not: "לא שותה/אוכלת",
  excessive: "מוגזם",
  // standing
  difficulty: "בקושי",
  barely: "בקושי רב",
  cannot: "לא מסוגלת",
  // fever
  mild: "קל",
  high: "גבוה",
  very_high: "גבוה מאוד",
  // swelling location / scratching
  leg: "רגל",
  abdomen: "בטן",
  face: "פנים",
  neck: "צוואר",
  ears: "אוזניים",
  eyes: "עיניים",
  skin: "עור",
  paws: "כפות",
  // walking ability
  limping: "צולעת",
  // walking after trauma
  yes: "כן",
  no: "לא",
  // urination
  straining: "מתאמצת",
  blood: "עם דם",
  // fallback categories
  breathing: "נשימה",
  cough: "שיעול",
  vomiting: "הקאות",
  diarrhea: "שלשול",
  weakness: "חולשה",
  pain: "כאב",
  bleeding: "דימום",
  appetite: "תיאבון",
  seizure: "פרכוסים",
  neuro: "נוירולוגי",
};

const OPTION_ICONS: Record<string, string> = {
  Dog: "🐩",
  Cat: "🐈",
};

function formatOption(opt: string): string {
  return OPTION_LABELS[opt] ?? opt.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function QuestionRenderer({ question, onAnswer, disabled = false }: Props) {
  const [numValue, setNumValue] = useState("");
  const [textValue, setTextValue] = useState("");
  const [chosen, setChosen] = useState<string | null>(null);

  function submitOnce(answer: unknown, display: string) {
    if (disabled) return;
    onAnswer(answer, display);
  }

  // --- Boolean: Yes / No ---
  if (question.type === "boolean") {
    return (
      <div className="flex gap-3 justify-center">
        {(["Yes", "No"] as const).map((label) => {
          const val = label === "Yes";
          const isChosen = chosen === label;
          return (
            <button
              key={label}
              onClick={() => {
                if (disabled || chosen) return;
                setChosen(label);
              submitOnce(val, label === "Yes" ? "כן" : "לא");
            }}
            disabled={disabled || chosen !== null}
            className={`px-12 py-3 rounded-xl text-base font-medium transition-all active:scale-95
              ${isChosen
                ? "bg-black text-white scale-95 opacity-80"
                : label === "Yes"
                ? "bg-gray-900 hover:bg-black text-white"
                : "bg-white hover:bg-gray-50 text-black border border-gray-300"}
              disabled:cursor-not-allowed disabled:opacity-50`}
          >
            {label === "Yes" ? "כן" : "לא"}
          </button>
          );
        })}
      </div>
    );
  }

  // --- Choice: grid of option buttons ---
  if (question.type === "choice" && question.options) {
    return (
      <div className="flex flex-wrap gap-2 justify-center">
        {question.options.map((opt) => {
          const isChosen = chosen === opt;
          return (
            <button
              key={opt}
              onClick={() => {
                if (disabled || chosen) return;
                setChosen(opt);
                submitOnce(opt, formatOption(opt));
              }}
              disabled={disabled || chosen !== null}
              className={`px-4 py-2.5 rounded-xl text-base font-medium transition-all active:scale-95 border
                ${isChosen
                  ? "bg-black border-black text-white scale-95 opacity-80"
                  : "bg-white border-gray-300 hover:border-gray-400 hover:bg-gray-50 text-black"}
                disabled:cursor-not-allowed disabled:opacity-50`}
            >
              {OPTION_ICONS[opt]
                ? <span className="flex items-center gap-3">{formatOption(opt)}<span className="leading-none -mr-1">{OPTION_ICONS[opt]}</span></span>
                : formatOption(opt)
              }
            </button>
          );
        })}
      </div>
    );
  }

  // --- Numeric ---
  if (question.type === "numeric") {
    const isAge = question.id === "age";
    const isWeight = question.id === "weight_kg";
    const maxVal = isAge ? 20 : isWeight ? 90 : undefined;
    const val = parseFloat(numValue);
    const isValid = !isNaN(val) && val > 0 && (maxVal === undefined || val <= maxVal);

    return (
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (isValid && !disabled) submitOnce(val, numValue);
        }}
        className="flex gap-2"
      >
        <input
          type="number"
          step="1"
          min="1"
          max={maxVal}
          value={numValue}
          onChange={(e) => setNumValue(e.target.value)}
          placeholder="הכנס מספר…"
          autoFocus
          disabled={disabled}
          className="flex-1 bg-white border border-gray-300 focus:border-gray-500 rounded-xl px-4 py-3 text-base text-black placeholder-gray-400 outline-none transition-colors disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={disabled || !isValid}
          className="px-6 py-3 bg-black hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed rounded-xl text-base font-semibold text-white transition-all active:scale-95 border border-black"
        >
          הבא ←
        </button>
      </form>
    );
  }

  // --- Text (default) ---
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (textValue.trim() && !disabled) submitOnce(textValue.trim(), textValue.trim());
      }}
      className="flex gap-2"
    >
      <input
        type="text"
        value={textValue}
        onChange={(e) => setTextValue(e.target.value)}
        placeholder="הקלד/י תשובה…"
        autoFocus
        disabled={disabled}
        className="flex-1 bg-white border border-gray-300 focus:border-gray-500 rounded-xl px-4 py-3 text-base text-black placeholder-gray-400 outline-none transition-colors disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !textValue.trim()}
        className="px-6 py-3 bg-black hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed rounded-xl text-base font-semibold text-white transition-all active:scale-95 border border-black"
      >
        הבא ←
      </button>
    </form>
  );
}

