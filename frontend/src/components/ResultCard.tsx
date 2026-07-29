import type { ChatResult } from "../api/chatApi";

interface Props {
  result: ChatResult;
  onRestart: () => void;
}

const SYMPTOM_TRANSLATIONS: Array<[string, string]> = [
  ["loss of consciousness", "אובדן הכרה"],
  ["severe bleeding", "דימום חמור"],
  ["open-mouth breathing", "נשימה בפה פתוח"],
  ["labored breathing", "נשימה מאומצת"],
  ["abnormal breath sounds", "קולות נשימה חריגים"],
  ["nasal discharge", "הפרשות מהאף"],
  ["blue gums", "חניכיים כחולות"],
  ["pale gums", "חניכיים חיוורות"],
  ["repeated seizures", "פרכוסים חוזרים"],
  ["blood in vomit", "דם בהקאה"],
  ["bloody diarrhea", "שלשול דמי"],
  ["blood in urine", "דם בשתן"],
  ["not urinating", "אי מתן שתן"],
  ["straining to urinate", "מאמץ במתן שתן"],
  ["swollen abdomen", "בטן נפוחה"],
  ["abdominal pain", "כאבי בטן"],
  ["weight loss", "ירידה במשקל"],
  ["cannot stand", "לא מסוגל לעמוד"],
  ["cannot walk", "לא מסוגל ללכת"],
  ["balance loss", "אובדן שיווי משקל"],
  ["head tilt", "הטיית ראש"],
  ["first seizure", "פרכוס ראשון"],
  ["reduced appetite", "תיאבון מופחת"],
  ["loss of appetite", "חוסר תיאבון"],
  ["not drinking", "לא שותה"],
  ["excessive drinking", "שתייה מוגברת"],
  ["sudden collapse", "קריסה פתאומית"],
  ["unresponsive", "לא מגיב"],
  ["collapse", "קריסה"],
  ["convulsions", "עוויתות"],
  ["seizure", "פרכוס"],
  ["coughing", "שיעול"],
  ["sneezing", "התעטשות"],
  ["vomiting", "הקאה"],
  ["diarrhea", "שלשול"],
  ["lethargy", "אפאטיות"],
  ["weakness", "חולשה"],
  ["tremor", "רעידות"],
  ["drooling", "ריור"],
  ["fever", "חום"],
  ["high fever", "חום גבוה"],
  ["bleeding", "דימום"],
  ["trauma", "טראומה"],
  ["wound", "פצע"],
  ["pain", "כאב"],
  ["lameness", "צליעה"],
  ["stiffness", "נוקשות"],
  ["swelling", "נפיחות"],
  ["scratching", "גרד"],
  ["eye discharge", "הפרשות מהעין"],
  ["eye problem", "בעיה בעין"],
  ["skin lesion", "נגע עורי"],
];

function escapeRegex(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function extractHebrewSymptoms(alltext: string): string[] {
  const source = alltext.toLowerCase();
  const matches: Array<{ start: number; end: number; hebrew: string; len: number }> = [];

  for (const [english, hebrew] of SYMPTOM_TRANSLATIONS) {
    const pattern = new RegExp(`\\b${escapeRegex(english)}\\b`, "g");
    let hit = pattern.exec(source);
    while (hit) {
      const start = hit.index;
      const end = start + english.length;
      matches.push({ start, end, hebrew, len: english.length });
      hit = pattern.exec(source);
    }
  }

  matches.sort((a, b) => {
    if (a.start !== b.start) return a.start - b.start;
    return b.len - a.len;
  });

  const selected: string[] = [];
  let cursor = -1;
  for (const m of matches) {
    if (m.start < cursor) continue;
    selected.push(m.hebrew);
    cursor = m.end;
  }

  // Remove duplicates while preserving order
  return [...new Set(selected)];
}

/** Translate alltext summary from canonical English symptoms to Hebrew */
function formatSummary(alltext: string): string {
  if (!alltext) return "";

  const parsedSymptoms = extractHebrewSymptoms(alltext);
  if (parsedSymptoms.length > 0) {
    return parsedSymptoms.join(", ");
  }

  let translated = alltext.toLowerCase();

  for (const [english, hebrew] of SYMPTOM_TRANSLATIONS) {
    const pattern = new RegExp(`\\b${escapeRegex(english)}\\b`, "g");
    translated = translated.replace(pattern, hebrew);
  }

  return translated;
}

export default function ResultCard({ result, onRestart }: Props) {
  const isEmergency = result.prediction === "Emergency";
  const summary = result.alltext ? formatSummary(result.alltext) : "";

  return (
    <div
      className={`rounded-2xl border p-5 flex flex-col gap-4 ${
        isEmergency ? "bg-red-50 border-red-200" : "bg-green-50 border-green-200"
      }`}
    >
      {/* ── 1. Prediction badge ── */}
      <div className="flex items-center gap-3">
        <span className="text-4xl">{isEmergency ? "🚨" : "✅"}</span>
        <div>
          <p className="text-sm text-gray-500 uppercase tracking-widest mb-0.5">
            תוצאת הטריאז'
          </p>
          <h2
            className={`text-3xl font-extrabold tracking-tight ${
              isEmergency ? "text-red-600" : "text-green-600"
            }`}
          >
            {isEmergency ? "חירום" : "לא דחוף"}
          </h2>
        </div>
      </div>

      {/* ── 2. Interpretation ── */}
      <div
        className={`rounded-xl px-4 py-3 text-base leading-relaxed ${
          isEmergency
            ? "bg-red-100/80 text-red-700"
            : "bg-green-100/80 text-green-700"
        }`}
      >
        {isEmergency ? (
          <>
            <span className="font-semibold">זוהה דפוס סיכון גבוה.</span>{" "}
            המערכת זיהתה תסמינים הקשורים בדרך כלל למצבי חירום. פנה לווטרינר בהקדם האפשרי.
          </>
        ) : (
          <>
            <span className="font-semibold">לא זוהה דפוס חירום.</span>{" "}
            המערכת לא זיהתה אישור חירום בהתבסס על התסמינים שדווחו. המשך לעקוב אחר החיה ופנה לווטרינר אם המצב משתנה או נמשך.
          </>
        )}
      </div>

      {/* ── 3. Symptom summary ── */}
      {summary && (
        <div className="bg-white border border-gray-200 rounded-xl px-4 py-3">
          <p className="text-sm text-gray-500 uppercase tracking-wider mb-2">
            סיכום תסמינים שדווח
          </p>
          <p className="text-base text-black leading-relaxed">
            {summary}
          </p>
        </div>
      )}

      {/* ── 4. Safety note ── */}
      <div className="flex items-start gap-2 bg-white border border-gray-200 rounded-xl px-3 py-2.5">
        <span className="text-yellow-500 text-base mt-0.5">⚠️</span>
        <p className="text-sm text-gray-700 leading-relaxed">
          כלי זה הוא עזר להחלטה בלבד ואינו{" "}
          <span className="font-semibold text-black">מחליף</span> ווטרינר מוסמך.
        </p>
      </div>

      {/* ── 5. Restart ── */}
      <button
        onClick={onRestart}
        className="w-full py-3 bg-black hover:bg-gray-800 active:scale-95 rounded-xl text-base font-semibold text-white transition-all shadow-md"
      >
        ↺ התחל הערכה חדשה
      </button>
    </div>
  );
}


