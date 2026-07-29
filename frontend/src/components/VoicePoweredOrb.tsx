/**
 * VoicePoweredOrb — visual-only animated orb component.
 *
 * If you have a custom VoicePoweredOrb to use, replace the contents of this
 * file with it and keep the same Props interface so App.tsx continues to work.
 *
 * phase:
 *   loading  — gray, static
 *   chatting — blue, pulsing rings (active)
 *   done     — green, settled glow
 *   error    — red, static
 */

type OrbPhase = "loading" | "chatting" | "done" | "error";

interface Props {
  phase: OrbPhase;
}

const CORE_COLOR: Record<OrbPhase, string> = {
  loading: "from-gray-600 to-gray-700",
  chatting: "from-blue-500 to-indigo-600",
  done: "from-green-500 to-emerald-600",
  error: "from-red-500 to-rose-600",
};

const GLOW_COLOR: Record<OrbPhase, string> = {
  loading: "shadow-gray-700/50",
  chatting: "shadow-blue-500/60",
  done: "shadow-green-500/60",
  error: "shadow-red-500/60",
};

const RING_COLOR: Record<OrbPhase, string> = {
  loading: "bg-gray-500",
  chatting: "bg-blue-400",
  done: "bg-green-400",
  error: "bg-red-400",
};

export default function VoicePoweredOrb({ phase }: Props) {
  return (
    <div className="relative flex items-center justify-center w-36 h-36">
      {/* Outer pulse ring — only while chatting */}
      {phase === "chatting" && (
        <>
          <span
            className={`absolute inset-0 rounded-full ${RING_COLOR[phase]} opacity-20 animate-ping`}
          />
          <span
            className={`absolute w-28 h-28 rounded-full ${RING_COLOR[phase]} opacity-10 animate-ping`}
            style={{ animationDelay: "400ms" }}
          />
        </>
      )}

      {/* Done settled ring */}
      {phase === "done" && (
        <span className="absolute inset-0 rounded-full bg-green-500 opacity-10 scale-110" />
      )}

      {/* Core orb */}
      <div
        className={`relative w-24 h-24 rounded-full bg-gradient-to-br ${CORE_COLOR[phase]} shadow-2xl ${GLOW_COLOR[phase]} flex items-center justify-center transition-all duration-700`}
        style={{ boxShadow: undefined }}
      >
        {/* Inner gloss highlight */}
        <div className="absolute top-3 left-4 w-8 h-8 rounded-full bg-white/20 blur-sm" />

        {/* Center icon */}
        <div className="relative z-10">
          {phase === "loading" && (
            <svg className="w-8 h-8 text-white/60 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
          )}
          {phase === "chatting" && (
            <svg className="w-8 h-8 text-white/90" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-3 3v-3z" />
            </svg>
          )}
          {phase === "done" && (
            <svg className="w-8 h-8 text-white/90" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          )}
          {phase === "error" && (
            <svg className="w-8 h-8 text-white/90" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            </svg>
          )}
        </div>
      </div>
    </div>
  );
}
