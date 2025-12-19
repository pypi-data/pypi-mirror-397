"""Cognitive thinking models and reasoning templates.

These tools generate structured prompts that enforce intent clarification,
logic verification, and correction via diverse thinking patterns.
"""

from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ValidationError


class UnderstandQuestionInput(BaseModel):
    question: str = Field(..., min_length=3, description="The raw user ask to unpack.")
    context: Optional[str] = Field(None, description="Optional background knowledge.")
    constraints: Optional[str] = Field(None, description="Explicit limits or success criteria.")


class VerifyLogicInput(BaseModel):
    claim: str = Field(..., min_length=3, description="The headline answer or assertion to validate.")
    reasoning_trace: str = Field(..., min_length=10, description="The supporting chain-of-thought.")
    constraints: Optional[str] = Field(None, description="Optional guardrails.")


class BacktrackingInput(BaseModel):
    objective: str = Field(..., min_length=3, description="Overall goal to satisfy.")
    failed_step: str = Field(..., min_length=3, description="The step or subgoal that failed.")
    trace: Optional[str] = Field(None, description="Optional reasoning trace leading to the failure.")
    constraints: Optional[str] = Field(None, description="Guardrails or requirements.")


class SymbolicAbstractInput(BaseModel):
    expression: str = Field(..., min_length=1, description="The raw text or equation to abstract.")
    mapping_hint: Optional[str] = Field(None, description="Optional guidance for token-to-symbol mapping.")
    goal: Optional[str] = Field(None, description="Optional downstream task.")


def register_thinking_models(mcp: FastMCP) -> None:
    """Register cognitive thinking-model tools on the provided MCP instance.

    Args:
        mcp: Active FastMCP instance to attach tools to.
    """

    @mcp.tool()
    def understand_question(
        question: str,
        context: Optional[str] = None,
        constraints: Optional[str] = None,
    ) -> str:
        """Produce a protocol shell to decompose a user question.

        Args:
            question: The raw user ask to unpack.
            context: Optional background knowledge or situational frame.
            constraints: Explicit limits or success criteria.

        Returns:
            A structured prompt guiding the model to restate intent, surface
            constraints, and prepare clarifying questions before acting.
        """
        # Validate input using Pydantic
        try:
            model = UnderstandQuestionInput(
                question=question, context=context, constraints=constraints
            )
        except ValidationError as e:
            return f"Input Validation Error: {e}"

        normalized_context = model.context or "<none>"
        normalized_constraints = model.constraints or "<none>"

        template = """
/reasoning.understand_question{{
    intent="Clarify the ask before solving by isolating intent, constraints, and required outputs",
    input={{
        question="{question}",
        context="{context}",
        constraints="{constraints}"
    }},
    process=[
        /intent_map{{action="Restate the core ask and target outcome"}},
        /constraints{{action="List explicit and implicit constraints"}},
        /decomposition{{action="Break request into solvable sub-goals"}},
        /risk_check{{action="Flag ambiguity or missing data"}}
    ],
    output={{
        intent="Single sentence goal statement",
        constraints="Bullet list of must-haves and guardrails",
        clarifications="Questions to close gaps before execution",
        proposed_plan="Initial steps or protocol to proceed"
    }}
}}
"""
        return template.format(
            question=model.question,
            context=normalized_context,
            constraints=normalized_constraints,
        )

    @mcp.tool()
    def verify_logic(
        claim: str,
        reasoning_trace: str,
        constraints: Optional[str] = None,
    ) -> str:
        """Generate a verification protocol for a reasoning trace.

        Args:
            claim: The headline answer or assertion to validate.
            reasoning_trace: The supporting chain-of-thought or proof steps.
            constraints: Optional guardrails (requirements, risk limits).

        Returns:
            Structured prompt that audits assumptions, inference steps, and
            evidence, then proposes patches for any defects.
        """
        try:
            model = VerifyLogicInput(
                claim=claim, reasoning_trace=reasoning_trace, constraints=constraints
            )
        except ValidationError as e:
            return f"Input Validation Error: {e}"

        normalized_constraints = model.constraints or "<none>"

        template = """
/reasoning.verify_logic{{
    intent="Audit a reasoning trace for validity, completeness, and constraint alignment",
    input={{
        claim="{claim}",
        reasoning_trace="{reasoning_trace}",
        constraints="{constraints}"
    }},
    process=[
        /premise_check{{action="List premises and mark which are stated vs. assumed"}},
        /consistency{{action="Check each step for logical validity and missing links"}},
        /evidence_map{{action="Match claims to evidence or note gaps"}},
        /contra{{action="Search for contradictions or constraint violations"}},
        /repair_plan{{action="Suggest minimal edits or extra steps to fix defects"}}
    ],
    output={{
        verdict="pass|fail with one sentence rationale",
        defect_log="Numbered list of issues with locations in the trace",
        patched_plan="Revised steps or guardrails to repair the reasoning",
        confidence="0-1 score grounded in evidence coverage and consistency"
    }}
}}
"""
        return template.format(
            claim=model.claim,
            reasoning_trace=model.reasoning_trace,
            constraints=normalized_constraints,
        )

    @mcp.tool()
    def backtracking(
        objective: str,
        failed_step: str,
        trace: Optional[str] = None,
        constraints: Optional[str] = None,
    ) -> str:
        """Produce a recursive backtracking scaffold for error correction.

        Args:
            objective: Overall goal to satisfy.
            failed_step: The step or subgoal that failed.
            trace: Optional reasoning trace leading to the failure.
            constraints: Guardrails or requirements to respect.

        Returns:
            Structured prompt that rewinds to last stable state, explores
            alternatives, and proposes a patched plan.
        """
        try:
            model = BacktrackingInput(
                objective=objective,
                failed_step=failed_step,
                trace=trace,
                constraints=constraints,
            )
        except ValidationError as e:
            return f"Input Validation Error: {e}"

        normalized_trace = model.trace or "<none>"
        normalized_constraints = model.constraints or "<none>"

        template = """
/reasoning.backtracking{{
    intent="Recover from failure by stepping back, exploring alternatives, and re-planning",
    input={{
        objective="{objective}",
        failed_step="{failed_step}",
        trace="{trace}",
        constraints="{constraints}"
    }},
    process=[
        /locate_break{{action="Identify point of failure and prior valid state"}},
        /hypothesize{{action="List alternative branches with pros/cons"}},
        /test_branch{{action="Mentally simulate top alternatives against constraints"}},
        /select{{action="Choose next branch with rationale"}},
        /plan_forward{{action="Lay out next steps with checkpoints"}}
    ],
    output={{
        recovery_plan="Steps to proceed from stable state",
        branch_rationale="Why this branch was chosen",
        risks="Remaining risks or unknowns",
        checkpoints="Where to re-verify along the way"
    }}
}}
"""
        return template.format(
            objective=model.objective,
            failed_step=model.failed_step,
            trace=normalized_trace,
            constraints=normalized_constraints,
        )

    @mcp.tool()
    def symbolic_abstract(
        expression: str,
        mapping_hint: Optional[str] = None,
        goal: Optional[str] = None,
    ) -> str:
        """Convert a concrete expression into abstract variables for reasoning.

        Args:
            expression: The raw text or equation to abstract.
            mapping_hint: Optional guidance for token-to-symbol mapping.
            goal: Optional downstream task (e.g., simplify, prove, generalize).

        Returns:
            Structured prompt that maps tokens to symbols, restates the problem
            abstractly, and provides a reversible mapping table.
        """
        try:
            model = SymbolicAbstractInput(
                expression=expression, mapping_hint=mapping_hint, goal=goal
            )
        except ValidationError as e:
            return f"Input Validation Error: {e}"

        normalized_hint = model.mapping_hint or "<none>"
        normalized_goal = model.goal or "<general>"

        template = """
/symbolic.abstract{{
    intent="Abstract concrete tokens into symbolic variables to enable general reasoning",
    input={{
        expression="{expression}",
        mapping_hint="{mapping_hint}",
        goal="{goal}"
    }},
    process=[
        /tokenize{{action="Identify meaningful tokens/entities in the expression"}},
        /assign_symbols{{action="Map tokens to abstract symbols with reversible table"}},
        /restatement{{action="Restate the problem using only symbols"}},
        /constraints{{action="Preserve constraints or relationships between symbols"}}
    ],
    output={{
        abstract_form="Symbolic restatement of the expression/problem",
        symbol_table="Mapping of symbols -> original tokens",
        invariants="Constraints/relations maintained in abstraction",
        next_steps="How to use the abstraction for the stated goal"
    }}
}}
"""
        return template.format(
            expression=model.expression,
            mapping_hint=normalized_hint,
            goal=normalized_goal,
        )


__all__ = ["register_thinking_models"]
