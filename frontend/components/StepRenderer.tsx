"use client";

import { InlineMath } from "react-katex";
import "katex/dist/katex.min.css";
import { Step } from "@/lib/types";

function renderMixedContent(text: string) {
  const parts = text.split(/(\$[^$]+\$)/g);
  return parts.map((part, i) => {
    if (part.startsWith("$") && part.endsWith("$")) {
      return <InlineMath key={i} math={part.slice(1, -1)} />;
    }
    return <span key={i}>{part}</span>;
  });
}

export default function StepRenderer({ step }: { step: Step }) {
  const isError = step.result?.startsWith("ERROR");

  return (
    <div className={`p-4 border-l-4 rounded-r-lg mb-3 ${isError ? "border-red-500 bg-red-50" : "border-blue-500 bg-blue-50"}`}>
      <div className="text-sm text-gray-500 mb-1">Step {step.step_id}</div>
      <div className="text-lg text-gray-900 font-medium">{renderMixedContent(step.description_latex)}</div>
      {step.result && (
        <div className={`mt-2 text-sm font-mono ${isError ? "text-red-700" : "text-gray-700"}`}>
          → {step.result}
        </div>
      )}
    </div>
  );
}