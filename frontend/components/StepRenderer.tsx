// frontend/components/StepRenderer.tsx
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
    <div
      className={`rounded-lg px-4 py-3 ${
        isError ? "bg-[#2A1414] border border-[#8B3A3A]" : "bg-[#F5F0E4]"
      }`}
    >
      <div className={`text-xs mb-1 ${isError ? "text-[#D99]" : "text-[#8A7F66]"}`}>
        Step {step.step_id}
      </div>
      <div className={`font-serif text-[15px] ${isError ? "text-[#E88]" : "text-[#2A2114]"}`}>
        {renderMixedContent(step.description_latex)}
      </div>
      {step.result && (
        <div className={`mt-1.5 text-sm font-mono ${isError ? "text-[#D99]" : "text-[#5C5340]"}`}>
          → {step.result}
        </div>
      )}
    </div>
  );
}