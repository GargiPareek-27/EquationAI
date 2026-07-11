"use client";

import { useState } from "react";

export default function ProblemInput({ onSubmit, loading }: { onSubmit: (text: string) => void; loading: boolean }) {
  const [text, setText] = useState("");

  return (
    <div className="w-full max-w-2xl">
      <textarea
        className="w-full p-4 border border-gray-300 rounded-lg text-lg resize-none"
        rows={4}
        placeholder="Enter a math problem, e.g. 'Sara has 3 times as many apples as Tom...'"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button
        onClick={() => onSubmit(text)}
        disabled={loading || !text.trim()}
        className="mt-3 px-6 py-2 bg-blue-600 text-white rounded-lg font-medium disabled:bg-gray-300"
      >
        {loading ? "Solving..." : "Solve"}
      </button>
    </div>
  );
}