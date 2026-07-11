// frontend/lib/api-client.ts
import { SolutionPlan } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export class SolveError extends Error {
  constructor(message: string, public isNetworkError: boolean = false) {
    super(message);
    this.name = "SolveError";
  }
}

export async function solveProblem(problemText: string): Promise<SolutionPlan> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/solve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ problem_text: problemText }),
    });
  } catch (networkErr) {
    // fetch() itself throwing means the server is unreachable — a genuinely
    // different situation from the server responding with an error.
    throw new SolveError(
      "Couldn't reach the server. Make sure the backend is running.",
      true
    );
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new SolveError(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}