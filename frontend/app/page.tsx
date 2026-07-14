// frontend/app/page.tsx
"use client";

import { useState } from "react";
import ProblemInput from "@/components/ProblemInput";
import StepRenderer from "@/components/StepRenderer";
import ClarificationNeeded from "@/components/ClarificationNeeded";
import { solveProblem, SolveError } from "@/lib/api-client";
import { SolutionPlan } from "@/lib/types";

export default function Home() {
  const [plan, setPlan] = useState<SolutionPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isNetworkError, setIsNetworkError] = useState(false);

  async function handleSubmit(problemText: string) {
    setLoading(true);
    setError(null);
    setIsNetworkError(false);
    setPlan(null);
    try {
      const result = await solveProblem(problemText);
      setPlan(result);
    } catch (e) {
      if (e instanceof SolveError) {
        setError(e.message);
        setIsNetworkError(e.isNetworkError);
      } else {
        setError("Something unexpected went wrong.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex flex-col items-center min-h-screen px-6 py-16 gap-8">
      <div className="text-center mb-2">
        <h1 className="font-serif text-4xl text-[#F5F0E4] tracking-tight">EquationAI</h1>
        <p className="text-[#8B96A8] text-sm mt-2">Verified step-by-step mathematical reasoning</p>
      </div>

      <ProblemInput onSubmit={handleSubmit} loading={loading} />

      {error && (
        <div className="w-full max-w-2xl p-4 bg-[#2A1414] border border-[#8B3A3A] rounded-lg">
          <div className="font-medium text-[#E88] mb-1">
            {isNetworkError ? "Connection problem" : "Something went wrong"}
          </div>
          <div className="text-[#D99] text-sm">{error}</div>
        </div>
      )}

      {plan && !plan.is_solvable && (
        <ClarificationNeeded message={plan.clarification_needed} />
      )}

      {plan && plan.is_solvable && (
        <div className="w-full max-w-2xl flex flex-col gap-3">
          {plan.steps.map((step) => (
            <StepRenderer key={step.step_id} step={step} />
          ))}
          {plan.final_answer_variable && (
            <div className="flex items-center gap-2 bg-[#2A2010] border border-[#BA7517] rounded-lg px-4 py-3 mt-1">
              <svg className="w-4 h-4 text-[#EF9F27]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              <span className="font-serif text-[#FAC775] text-lg">
                Verified answer: {plan.steps[plan.steps.length - 1]?.result} {plan.final_answer_units}
              </span>
            </div>
          )}
        </div>
      )}
    </main>
  );
}