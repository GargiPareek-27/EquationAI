"use client";

import { useState } from "react";
import ProblemInput from "@/components/ProblemInput";
import StepRenderer from "@/components/StepRenderer";
import { solveProblem } from "@/lib/api-client";
import { SolutionPlan } from "@/lib/types";

export default function Home() {
  const [plan, setPlan] = useState<SolutionPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(problemText: string) {
    setLoading(true);
    setError(null);
    setPlan(null);
    try {
      const result = await solveProblem(problemText);
      setPlan(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex flex-col items-center min-h-screen p-8 gap-6">
      <h1 className="text-3xl font-bold">EquationAI</h1>
      <ProblemInput onSubmit={handleSubmit} loading={loading} />

      {error && <div className="text-red-600 max-w-2xl">{error}</div>}

      {plan && (
        <div className="w-full max-w-2xl">
          {plan.steps.map((step) => (
            <StepRenderer key={step.step_id} step={step} />
          ))}
          {plan.final_answer_variable && (
            <div className="mt-4 p-4 bg-green-50 border-l-4 border-green-500 rounded-r-lg font-semibold text-green-900 text-lg">
              Final answer: {plan.steps[plan.steps.length - 1]?.result} {plan.final_answer_units}
            </div>
          )}
        </div>
      )}
    </main>
  );
}