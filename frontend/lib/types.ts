export interface Variable {
  symbol: string;
  description: string;
  domain: string | null;
}

export interface Step {
  step_id: number;
  description_latex: string;
  sympy_expr: string;
  operation_type: string;
  depends_on: number[];
  result: string | null;
}

export interface SolutionPlan {
  problem_type: string;
  is_solvable: boolean;
  clarification_needed: string | null;
  variables: Variable[];
  steps: Step[];
  final_answer_variable: string | null;
  final_answer_units: string | null;
}