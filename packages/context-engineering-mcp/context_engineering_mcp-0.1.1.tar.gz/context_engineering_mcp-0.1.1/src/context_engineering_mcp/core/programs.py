"""Prompt program templates (Module 07).

These builders provide pseudo-code structures that guide LLMs through
multi-phase reasoning routines.
"""

from typing import Final

PROMPT_PROGRAM_DEBATE_TEMPLATE: Final[str] = """
// Prompt Program: Multi-Perspective Debate (Module 07)
// Based on the Debate Organ pattern for balanced analysis

function frame_debate_question(question, perspectives) {{
  return `
    Task: Set up a structured debate on the given question.
    Question: ${{question}}
    Perspectives to consider: ${{perspectives.join(', ')}}

    As the Moderator, please:
    1. Clarify the core question and any ambiguities
    2. Identify key dimensions of the debate
    3. Establish criteria for evaluating different viewpoints
    4. Set the scope and constraints for the discussion
  `;
}}

function generate_perspective(question, perspective_name, context) {{
  return `
    Task: Analyze the question from a specific perspective.
    Question: ${{question}}
    Perspective: ${{perspective_name}}
    Context: ${{context}}

    As the ${{perspective_name}} perspective, please:
    1. State your core position on this question
    2. Provide 2-3 key arguments supporting your position
    3. Identify assumptions underlying your perspective
    4. Acknowledge potential limitations or counterarguments
  `;
}}

function conduct_debate_round(question, perspectives_data, round_number) {{
  return `
    Task: Facilitate round ${{round_number}} of debate.
    Question: ${{question}}
    Previous Perspectives: ${{perspectives_data}}

    For this round, each perspective should:
    1. Respond to the strongest counterargument from other perspectives
    2. Refine or strengthen their position based on the discussion
    3. Find areas of agreement or common ground where applicable
    4. Raise new considerations not yet addressed
  `;
}}

function synthesize_debate(question, all_perspectives, debate_rounds) {{
  return `
    Task: Synthesize the multi-perspective debate into a balanced conclusion.
    Question: ${{question}}
    All Perspectives: ${{all_perspectives}}
    Debate Rounds: ${{debate_rounds}}

    Please provide:
    1. Summary of each major perspective and its key arguments
    2. Areas of consensus or common ground identified
    3. Irreconcilable differences and why they persist
    4. Nuanced conclusion that acknowledges complexity
    5. Recommendations or implications based on the full discussion
  `;
}}

// Main multi-perspective debate function
function run_multi_perspective_debate(question, perspectives = ["Optimistic", "Skeptical", "Pragmatic", "Ethical"], rounds = 2) {{
  // Phase 1: Frame the debate
  framing = LLM(frame_debate_question(question, perspectives));

  // Phase 2: Generate initial perspectives
  initial_perspectives = {{}};
  for (perspective of perspectives) {{
    initial_perspectives[perspective] = LLM(generate_perspective(question, perspective, framing));
  }}

  // Phase 3: Conduct debate rounds
  debate_history = [initial_perspectives];
  for (round = 1; round <= rounds; round++) {{
    round_results = LLM(conduct_debate_round(question, debate_history, round));
    debate_history.push(round_results);
  }}

  // Phase 4: Synthesize all perspectives
  synthesis = LLM(synthesize_debate(question, initial_perspectives, debate_history));

  return {{
    original_question: question,
    framing: framing,
    perspectives: initial_perspectives,
    debate_rounds: debate_history,
    synthesis: synthesis,
    num_perspectives: perspectives.length,
    num_rounds: rounds
  }};
}}
"""

PROMPT_PROGRAM_MATH_TEMPLATE: Final[str] = """
// Prompt Program: Math Solver (Module 07)

function understand_math_problem(problem) {
  return `
    Task: Analyze this math problem thoroughly before solving.
    Problem: ${problem}
    Please provide:
    1. What type of math problem is this?
    2. What are the key variables or unknowns?
    3. What are the given values or constraints?
    4. What formulas or methods will be relevant?
  `;
}

function plan_solution_steps(problem_analysis) {
  return `
    Task: Create a step-by-step plan to solve this math problem.
    Problem Analysis: ${problem_analysis}
    Please outline a specific sequence of steps to solve this problem.
  `;
}

function execute_solution(problem, solution_plan) {
  return `
    Task: Solve this math problem following the provided plan.
    Problem: ${problem}
    Solution Plan: ${solution_plan}
    Please show all work for each step.
  `;
}

function verify_solution(problem, solution) {
  return `
    Task: Verify the correctness of this math solution.
    Original Problem: ${problem}
    Proposed Solution: ${solution}
    Please check calculations and logic.
  `;
}

// Main problem-solving function
function solve_math_with_cognitive_tools(problem) {
  problem_analysis = LLM(understand_math_problem(problem));
  solution_plan = LLM(plan_solution_steps(problem_analysis));
  detailed_solution = LLM(execute_solution(problem, solution_plan));
  verification = LLM(verify_solution(problem, detailed_solution));

  return {
    original_problem: problem,
    analysis: problem_analysis,
    plan: solution_plan,
    solution: detailed_solution,
    verification: verification
  };
}
"""


def get_program_template(program_type: str) -> str:
    """Return a prompt program template for the requested type.

    Args:
        program_type: Identifier for the program to generate (e.g., "math", "debate").

    Returns:
        Template string for the requested program, or a generic message with
        the math solver template when unsupported.
    """
    normalized_type = program_type.lower()
    if normalized_type == "math":
        return PROMPT_PROGRAM_MATH_TEMPLATE
    elif normalized_type == "debate":
        return PROMPT_PROGRAM_DEBATE_TEMPLATE
    return (
        f"// Program type '{program_type}' not yet implemented. Returning generic structure.\\n"
        + PROMPT_PROGRAM_MATH_TEMPLATE
    )


__all__ = [
    "PROMPT_PROGRAM_MATH_TEMPLATE",
    "PROMPT_PROGRAM_DEBATE_TEMPLATE",
    "get_program_template",
]
