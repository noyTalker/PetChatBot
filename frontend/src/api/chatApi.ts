export interface Question {
  id: string;
  text: string;
  type: "choice" | "boolean" | "numeric" | "text";
  options: string[] | null;
}

export interface StartResponse {
  session_id: string;
  question: Question;
}

export interface ChatResult {
  done: true;
  prediction: string;
  alltext: string;
  answers: Record<string, unknown>;
}

export interface NextQuestionResponse {
  done: false;
  question: Question;
}

export type AnswerResponse = NextQuestionResponse | ChatResult;

const API_BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
const API_TIMEOUT_MS = 90_000;

async function apiFetch(path: string, init?: RequestInit) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT_MS);

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
    });
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    return res;
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error("timeout");
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

// ---------------------------------------------------------------------------
// API calls — local dev uses Vite proxy; production uses VITE_API_URL
// ---------------------------------------------------------------------------

export async function startChat(): Promise<StartResponse> {
  const res = await apiFetch("/chat/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  return res.json();
}

export async function answerQuestion(
  sessionId: string,
  answer: unknown
): Promise<AnswerResponse> {
  const res = await apiFetch("/chat/answer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, answer }),
  });
  return res.json();
}
