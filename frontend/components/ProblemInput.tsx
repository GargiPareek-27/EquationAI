// frontend/components/ProblemInput.tsx
"use client";

import { useState } from "react";

export default function ProblemInput({ onSubmit, loading }: { onSubmit: (text: string) => void; loading: boolean }) {
  const [text, setText] = useState("");

  return (
    <div className="w-full max-w-2xl">
      <textarea
        className="w-full p-4 bg-[#16233A] border border-[#2A3A54] rounded-lg text-[#D8DEE9] text-[15px] placeholder-[#5C6B85] resize-none focus:outline-none focus:border-[#BA7517] transition-colors"
        rows={4}
        placeholder="Enter a math problem, e.g. 'Sara has 3 times as many apples as Tom...'"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button
        onClick={() => onSubmit(text)}
        disabled={loading || !text.trim()}
        className="mt-3 px-6 py-2 bg-[#BA7517] text-[#1A1206] rounded-lg font-medium disabled:bg-[#3A3529] disabled:text-[#6B6455] hover:bg-[#D08A1F] transition-colors"
      >
        {loading ? "Solving…" : "Solve"}
      </button>
    </div>
  );
}