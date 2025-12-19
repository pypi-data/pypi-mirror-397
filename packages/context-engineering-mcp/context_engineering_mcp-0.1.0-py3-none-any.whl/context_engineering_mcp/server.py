from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ValidationError

from context_engineering_mcp.cognitive import register_thinking_models
from context_engineering_mcp.core import (
    CELL_PROTOCOL_REGISTRY,
    MOLECULAR_CONTEXT_FUNC,
    format_protocol_shell,
    get_cell_protocol_template,
    get_program_template,
    get_protocol_template,
)
from context_engineering_mcp.systems import get_organ_template

# Initialize FastMCP server
mcp = FastMCP("Context Engineering MCP")

# Register cognitive tools
register_thinking_models(mcp)


# --- Input Models ---

class TechniqueGuideInput(BaseModel):
    category: str = Field(
        "all",
        pattern="^(reasoning|workflow|code|project|all)$",
        description="Filter category."
    )


class TaskComplexityInput(BaseModel):
    task_description: str = Field(..., min_length=5, description="The user's prompt or task.")


class ProtocolShellInput(BaseModel):
    name: str = Field("MyProtocol", min_length=1, description="Protocol name.")
    intent: str | None = Field(None, description="Optional intent.")


class PromptProgramInput(BaseModel):
    program_type: str = Field("math", pattern="^(math|debate)$", description="Program type.")


class CellProtocolInput(BaseModel):
    name: str = Field("cell.protocol.key_value", min_length=1, description="Cell protocol name.")


class OrganInput(BaseModel):
    name: str = Field("debate_council", min_length=1, description="Organ name.")


class DesignArchitectureInput(BaseModel):
    goal: str = Field(..., min_length=5, description="The goal of the system to design.")
    constraints: str | None = Field(None, description="Optional constraints or preferences.")


# --- Tools ---


@mcp.tool()
def design_context_architecture(goal: str, constraints: str | None = None) -> dict:
    """
    Architects a custom context system based on a high-level goal (The Architect).
    Returns a blueprint of Sutra components (Molecules, Cells, Organs, Thinking Models).
    
    Use this when the user wants to build a persistent agent or complex workflow
    rather than solving a single immediate task.

    Args:
        goal: The user's objective (e.g., "Build a writing assistant that learns my style").
        constraints: Optional limits (e.g., "Must be lightweight").
    """
    try:
        model = DesignArchitectureInput(goal=goal, constraints=constraints)
    except ValidationError as e:
        return {"error": str(e)}

    g = model.goal.lower()
    c = (model.constraints or "").lower()

    # Blueprint Defaults
    blueprint = {
        "name": "Custom System",
        "rationale": "General purpose context structure.",
        "components": {
            "molecule": "Standard CoT",
            "cell": "cell.protocol.key_value",
            "organ": None,
            "cognitive": "reasoning.understand_question"
        }
    }

    if "lightweight" in c:
        blueprint["name"] += " (Light)"

    # Heuristic Architecture Logic
    if "debate" in g or "perspective" in g:
        blueprint["name"] = "Debate System"
        blueprint["components"]["organ"] = "organ.debate_council"
        blueprint["rationale"] = "Uses a multi-perspective organ to balance viewpoints."
    
    elif "research" in g or "report" in g or "synthesize" in g:
        blueprint["name"] = "Research Engine"
        blueprint["components"]["organ"] = "organ.research_synthesis"
        blueprint["components"]["cell"] = "cell.protocol.episodic" # Log research trails
        blueprint["rationale"] = "Combines a synthesis organ with episodic memory to track findings."

    elif "learn" in g or "remember" in g or "style" in g:
        blueprint["name"] = "Adaptive Assistant"
        blueprint["components"]["cell"] = "cell.protocol.windowed"
        blueprint["rationale"] = "Uses windowed memory to maintain recent context and style."

    elif "code" in g or "bug" in g or "review" in g:
        blueprint["name"] = "Code Auditor"
        blueprint["components"]["cognitive"] = "reasoning.verify_logic"
        blueprint["rationale"] = "Focuses on logic verification for code correctness."

    return blueprint


@mcp.tool()
def get_technique_guide(category: str = "all") -> str:
    """
    Returns a guide to available Context Engineering techniques (The Librarian).
    Use this to discover the best tool for a given task.

    Args:
        category: Filter by 'reasoning', 'workflow', 'code', 'project', or 'all'.
    """
    try:
        _ = TechniqueGuideInput(category=category)
    except ValidationError as e:
        return f"Input Validation Error: {e}"

    guide = """
    # Context Engineering Technique Guide

    | Category | Tool | Complexity | Best For |
    |----------|------|------------|----------|
    | **Architect** | `design_context_architecture` | Variable | **Constructor Mode**: Building custom agents/systems. |
    | **Router** | `analyze_task_complexity` | Low | **YOLO Mode**: Finding the right tool automatically. |
    | **Reasoning** | `reasoning.systematic` | High | Complex problems requiring step-by-step logic. |
    | **Reasoning** | `thinking.extended` | Very High | Deep exploration, trade-off analysis, simulation. |
    | **Workflow** | `workflow.test_driven` | High | Implementing features with TDD. |
    | **Code** | `code.analyze` | Medium | Understanding code structure and quality. |
    | **Project** | `project.explore` | Medium | Mapping a new codebase. |
    | **Basic** | `Standard Molecule` | Low | Simple pattern matching (use `get_molecular_template`). |

    **Usage:**
    - **YOLO Mode**: Call `analyze_task_complexity` to get a quick tool recommendation.
    - **Constructor Mode**: Call `design_context_architecture` to get a full system blueprint.
    """
    # Simple filtering (mock implementation for now based on description)
    # Ideally, this would filter the text, but the current implementation returns static text.
    # The validation ensures 'category' is safe.
    return guide


@mcp.tool()
def analyze_task_complexity(task_description: str) -> dict:
    """
    Analyzes a task to recommend the most efficient tool (The Router).

    Args:
        task_description: The user's prompt or task.
    """
    try:
        model = TaskComplexityInput(task_description=task_description)
    except ValidationError as e:
        return {"error": str(e)}

    task = model.task_description.lower()

    # Strategy: Constructor Mode (Build/Design)
    if any(w in task for w in ["build", "create", "design", "architect", "system", "bot", "assistant"]):
        return {
            "strategy": "constructor",
            "complexity": "Variable",
            "recommended_tool": "design_context_architecture",
            "reasoning": "User wants to build a system/agent. Use the Architect to design a blueprint."
        }

    # Strategy: YOLO Mode (Direct Solve)
    if any(w in task for w in ["project", "repo", "codebase", "architecture"]):
        return {
            "strategy": "yolo",
            "complexity": "Medium",
            "recommended_tool": "project.explore",
            "reasoning": "Task involves project-level understanding.",
        }
    elif any(w in task for w in ["test", "tdd", "verify"]):
        return {
            "strategy": "yolo",
            "complexity": "High",
            "recommended_tool": "workflow.test_driven",
            "reasoning": "Task involves testing or verification workflows.",
        }
    elif any(w in task for w in ["analyze", "reason", "think", "solve", "complex"]):
        return {
            "strategy": "yolo",
            "complexity": "High",
            "recommended_tool": "reasoning.systematic",
            "reasoning": "Task requires structured reasoning.",
        }
    else:
        return {
            "strategy": "yolo",
            "complexity": "Low",
            "recommended_tool": "Standard Molecule",
            "reasoning": "Task appears simple. Use a basic prompt or few-shot molecule.",
        }


@mcp.tool()
def get_protocol_shell(name: str = "MyProtocol", intent: str | None = None) -> str:
    """
    Returns a Protocol Shell. Can return a specific pre-defined template or a blank shell.

    Args:
        name: The name of the protocol (e.g., 'reasoning.systematic') OR a custom name.
        intent: (Optional) The intent if creating a custom shell.
    """
    try:
        model = ProtocolShellInput(name=name, intent=intent)
    except ValidationError as e:
        return f"Input Validation Error: {e}"

    template = get_protocol_template(model.name)
    if template:
        return template

    intent_str = model.intent or "Define your intent here"
    return format_protocol_shell(name=model.name, intent=intent_str)


@mcp.tool()
def get_molecular_template() -> str:
    """
    Returns the Python function for creating molecular contexts (Module 02).
    Use this to programmatically construct few-shot prompts.
    """
    return MOLECULAR_CONTEXT_FUNC


@mcp.tool()
def get_prompt_program(program_type: str = "math") -> str:
    """
    Returns a functional pseudo-code prompt template (Module 07).

    Args:
        program_type: The type of program ('math', 'debate').
    """
    try:
        model = PromptProgramInput(program_type=program_type)
    except ValidationError as e:
        return f"Input Validation Error: {e}"
        
    return get_program_template(model.program_type)


@mcp.tool()
def get_cell_protocol(name: str = "cell.protocol.key_value") -> str:
    """
    Returns a cell protocol template describing memory behaviors.

    Args:
        name: Identifier of the cell protocol (key_value, windowed, episodic).
    """
    try:
        model = CellProtocolInput(name=name)
    except ValidationError as e:
        return f"Input Validation Error: {e}"

    template = get_cell_protocol_template(model.name)
    if template:
        return template

    available = ", ".join(sorted(CELL_PROTOCOL_REGISTRY.keys()))
    return f"// Cell protocol '{model.name}' not found. Available protocols: {available}"


@mcp.tool()
def get_organ(name: str = "debate_council") -> str:
    """
    Returns an organ template for multi-agent orchestration (Layer 4).

    Organs combine programs and cells into cohesive workflows for complex tasks
    requiring multi-perspective analysis or collaborative reasoning.

    Args:
        name: Identifier of the organ ('debate_council' for multi-perspective debate).
    """
    try:
        model = OrganInput(name=name)
    except ValidationError as e:
        return f"Input Validation Error: {e}"

    return get_organ_template(model.name)


# --- Resources ---


@mcp.resource("context://molecules/cot")
def get_cot_molecules() -> str:
    """
    Returns Chain-of-Thought templates (Module 02).
    """
    return """
    # Chain of Thought Templates (Module 02)

    ## Standard CoT
    Q: [Question]
    A: Let's think step by step.
    1. [Step 1]
    2. [Step 2]
    Therefore, the answer is [Answer].

    ## Molecular Context Structure
    MOLECULE = [INSTRUCTION] + [EXAMPLES] + [CONTEXT] + [NEW INPUT]
    """


@mcp.resource("context://reference/layers")
def get_reference_layers() -> str:
    """
    Returns the Context Engineering Layer definitions.
    """
    return """
    # Context Engineering Layers

    1. Atoms: Basic units of meaning (Single Prompts).
    2. Molecules: Combinations of atoms (Few-Shot Templates).
    3. Cells: Functional units (Prompt Programs).
    4. Organs: Specialized structures (Protocol Shells).
    5. Systems: Interconnected networks (Agents).
    """


@mcp.resource("context://fields/resonance")
def get_neural_fields() -> str:
    """
    Returns Neural Field primitives (Module 08-10).
    """
    return """
    # Neural Field Protocols (Module 08-10)

    ## Resonance Field
    A structure for maintaining context persistence across long interaction horizons.

    [FIELD_DEFINITION]
    Type: Resonance
    Decay_Rate: Low
    Attractors: [Core Intent, User Preferences]
    """


def main():
    mcp.run()


if __name__ == "__main__":
    main()
