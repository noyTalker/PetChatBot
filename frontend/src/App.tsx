import { useState, useEffect, useRef } from "react";
import { startChat, answerQuestion } from "./api/chatApi";
import type { Question, ChatResult } from "./api/chatApi";
import VoicePoweredOrb from "./components/VoicePoweredOrb";
import QuestionRenderer from "./components/QuestionRenderer";
import ResultCard from "./components/ResultCard";

type Phase = "welcome" | "loading" | "chatting" | "done" | "error";
type OrbPhase = "loading" | "chatting" | "done" | "error";

interface Message {
  id: number;
  role: "bot" | "user";
  text: string;
}

let msgCounter = 0;

function newMsg(role: Message["role"], text: string): Message {
  return { id: ++msgCounter, role, text };
}

const BOT_DELAY_MS = 650;



export default function App() {
  const [phase, setPhase] = useState<Phase>("welcome");
  const [sessionId, setSessionId] = useState<string>("");
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [result, setResult] = useState<ChatResult | null>(null);
  const [waiting, setWaiting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll whenever messages change or typing indicator toggles
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, waiting]);

  async function startAssessment() {
    msgCounter = 0;
    setPhase("loading");
    setMessages([]);
    setResult(null);
    setCurrentQuestion(null);
    setWaiting(false);
    setErrorMsg("");
    try {
      const data = await startChat();
      setSessionId(data.session_id);
      setMessages([newMsg("bot", data.question.text)]);
      setCurrentQuestion(data.question);
      setPhase("chatting");
    } catch {
      setErrorMsg(
        "לא ניתן להתחבר לשרת. ודא שהשרת רץ על פורט 8000."
      );
      setPhase("error");
    }
  }

  function handleRestart() {
    msgCounter = 0;
    setPhase("welcome");
    setMessages([]);
    setResult(null);
    setCurrentQuestion(null);
    setWaiting(false);
    setErrorMsg("");
    setSessionId("");
  }

  async function handleAnswer(answer: unknown, displayText: string) {
    setMessages((prev) => [...prev, newMsg("user", displayText)]);
    setCurrentQuestion(null);
    setWaiting(true);

    try {
      const data = await answerQuestion(sessionId, answer);

      await new Promise((r) => setTimeout(r, BOT_DELAY_MS));

      setWaiting(false);

      if (data.done) {
        setResult(data);
        setPhase("done");
      } else {
        setMessages((prev) => [...prev, newMsg("bot", data.question.text)]);
        setCurrentQuestion(data.question);
      }
    } catch {
      setWaiting(false);
      setErrorMsg("משהו השתבש. נסה לרענן ולנסות שוב.");
      setPhase("error");
    }
  }

  // Map extended phase to the orb's accepted phase type
  const orbPhase: OrbPhase =
    phase === "welcome" ? "loading" :
    phase === "loading" ? "loading" :
    phase === "done" && result?.prediction === "Emergency" ? "error" :
    phase;

  return (
    <div className="h-screen text-black flex flex-col items-center overflow-hidden">

      {/* ─── Header ─── */}
      <header className="flex-shrink-0 flex flex-col items-center pt-7 pb-4 px-4 w-full max-w-xl border-b border-gray-200 bg-white/80 backdrop-blur-sm z-10">
        <VoicePoweredOrb phase={orbPhase} />
        <h1 className="text-2xl font-bold mt-4 tracking-tight text-black">
          מערכת Triage וטרינרית לסיווג רמת דחיפות רפואית
        </h1>
      </header>

      {/* ─── Welcome Screen ─── */}
      {phase === "welcome" && (
        <main className="flex-1 w-full max-w-xl px-4 flex flex-col items-center justify-center gap-5 z-10">
          <div className="welcome-in w-full bg-white border border-gray-200 rounded-2xl p-7 flex flex-col gap-5 text-center shadow-sm z-10">

            {/* ── Project title ── */}
            <div className="flex flex-col gap-1">
              <h2 className="text-xl font-bold text-black leading-snug">
                פיתוח צ'אטבוט לזיהוי מצבי חירום בחיות מחמד
              </h2>
              <p className="text-base text-gray-700 font-medium">
                על בסיס אלגוריתם למידה
              </p>
              <p className="text-sm text-gray-500 mt-1">
                קבוצה מספר 6 &mdash; בהנחייתו של מר אלכס גורביץ'
              </p>
            </div>

            <div className="w-full h-px bg-gray-200" />

            <div className="flex flex-col gap-2">
              <p className="text-lg font-medium text-black">
                התחלת הערכה מהירה של מצב חיית המחמד
              </p>
              <p className="text-sm text-gray-600 leading-relaxed">
                ענו על מספר שאלות לקבלת הערכת דחיפות ראשונית לטיפול וטרינרי מיידי
              </p>
            </div>
            <button
              onClick={startAssessment}
              className="w-1/2 mx-auto py-3.5 bg-black hover:bg-gray-800 active:scale-95 rounded-xl text-base font-semibold text-white transition-all shadow-md"
            >
              התחלה
            </button>
          </div>
          <p className="text-sm text-gray-500 text-center whitespace-nowrap">
            כלי זה נועד לעזר החלטה בלבד ואינו מהווה תחליף לייעוץ וטרינרי
          </p>
        </main>
      )}

      {/* ─── Loading transition ─── */}
      {phase === "loading" && (
        <main className="flex-1 w-full max-w-xl px-4 flex items-center justify-center z-10">
          <p className="text-gray-600 text-base">מתחבר…</p>
        </main>
      )}

      {/* ─── Chat + Input (chatting / done) ─── */}
      {(phase === "chatting" || phase === "done") && (
        <>
          {/* Scrollable chat transcript */}
          <main className="flex-1 overflow-y-auto w-full max-w-xl px-4 flex flex-col gap-3 pt-3 pb-2 z-10">
            {messages.length === 0 && (
              <p className="text-gray-500 text-sm text-center mt-6">
                הסייען ינחה אותך לאורך ההערכה.
              </p>
            )}

            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex msg-in ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {msg.role === "bot" && (
                  <div className="w-11 h-11 rounded-full bg-gray-100 border border-gray-200 flex-shrink-0 flex items-center justify-center mr-2 mt-0.5">
                    <span className="text-2xl">🐾</span>
                  </div>
                )}
                <div
                  className={`rounded-2xl px-4 py-3 max-w-[78%] text-base leading-relaxed ${
                    msg.role === "user"
                      ? "bg-gray-200 text-black rounded-br-none"
                      : "bg-white text-black border border-gray-200 shadow-sm rounded-bl-none"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {waiting && (
              <div className="flex justify-start msg-in">
                <div className="w-11 h-11 rounded-full bg-gray-100 border border-gray-200 flex-shrink-0 flex items-center justify-center mr-2 mt-0.5">
                  <span className="text-2xl">🐾</span>
                </div>
                <div className="bg-white border border-gray-200 shadow-sm rounded-2xl rounded-bl-none px-4 py-3">
                  <div className="flex gap-1.5 items-center h-4">
                    {[0, 150, 300].map((delay) => (
                      <span
                        key={delay}
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: `${delay}ms` }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}


            <div ref={bottomRef} />
          </main>

          {/* ─── Sticky input / result panel ─── */}
          <footer className="flex-shrink-0 w-full max-w-xl px-4 pb-6 pt-3 border-t border-gray-200 bg-white/90 backdrop-blur-sm z-10">
            {phase === "chatting" && currentQuestion && !waiting && (
              <div className="panel-up">
                <QuestionRenderer
                  key={currentQuestion.id}
                  question={currentQuestion}
                  onAnswer={handleAnswer}
                  disabled={waiting}
                />
              </div>
            )}

            {phase === "done" && result && (
              <div className="panel-up overflow-y-auto max-h-[38rem]">
                <ResultCard result={result} onRestart={handleRestart} />
              </div>
            )}
          </footer>
        </>
      )}

      {/* ─── Error state ─── */}
      {phase === "error" && (
        <main className="flex-1 w-full max-w-xl px-4 flex flex-col items-center justify-center gap-4 z-10">
          <div className="w-full bg-red-50 border border-red-200 rounded-2xl p-5 text-black text-base text-center leading-relaxed">
            {errorMsg}
          </div>
          <button
            onClick={handleRestart}
            className="px-6 py-3 bg-white hover:bg-gray-50 active:scale-95 rounded-xl text-base font-medium text-black transition-all border border-gray-300"
          >
            → חזור להתחלה
          </button>
        </main>
      )}
    </div>
  );
}
