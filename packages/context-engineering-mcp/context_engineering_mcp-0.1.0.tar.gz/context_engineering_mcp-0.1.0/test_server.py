from context_engineering_mcp.server import (
    get_protocol_shell,
    get_prompt_program,
    get_molecular_template,
    get_cot_molecules,
    get_reference_layers,
    get_technique_guide,
    analyze_task_complexity,
    get_organ,
)


def test_get_protocol_shell():
    """Test that protocol shell returns correct structure."""
    intent = "Test Intent"
    name = "TestProtocol"
    result = get_protocol_shell(intent=intent, name=name)

    assert "/protocol.TestProtocol" in result
    assert 'intent="Test Intent"' in result
    assert "input={" in result
    assert "output={" in result


def test_get_technique_guide():
    result = get_technique_guide()
    assert "Context Engineering Technique Guide" in result
    assert "| Category | Tool |" in result
    assert "reasoning.systematic" in result


def test_analyze_task_complexity():
    # Test Constructor Mode
    constructor = analyze_task_complexity("Build a research assistant bot")
    assert constructor["strategy"] == "constructor"
    assert constructor["recommended_tool"] == "design_context_architecture"

    # Test YOLO Mode (High)
    high = analyze_task_complexity(
        "I need to refactor this entire codebase and add tests"
    )
    assert high["strategy"] == "yolo"
    assert (
        high["complexity"] == "High" or high["complexity"] == "Medium"
    )

    # Test YOLO Mode (Low)
    low = analyze_task_complexity("What is 2+2?")
    assert low["strategy"] == "yolo"
    assert low["complexity"] == "Low"


def test_design_context_architecture():
    """Test the architect tool."""
    from context_engineering_mcp.server import design_context_architecture
    
    # Test Debate System
    debate = design_context_architecture(goal="Build a debate bot")
    assert debate["name"] == "Debate System"
    assert debate["components"]["organ"] == "organ.debate_council"
    
    # Test Research Engine
    research = design_context_architecture(goal="Create a research assistant")
    assert research["name"] == "Research Engine"
    assert research["components"]["organ"] == "organ.research_synthesis"
    
    # Test Default
    default = design_context_architecture(goal="Just something random")
    assert default["name"] == "Custom System"
    assert default["components"]["molecule"] == "Standard CoT"


def test_get_protocol_shell_registry():
    # Test retrieving a specific template from registry
    result = get_protocol_shell(name="reasoning.systematic")
    assert 'intent="Break down complex problems' in result

    # Test generic fallback
    generic = get_protocol_shell(name="CustomProtocol", intent="Testing")
    assert 'intent="Testing"' in generic
    assert "output={" in result


def test_get_prompt_program_math():
    """Test that math prompt program returns correct template."""
    result = get_prompt_program(program_type="math")

    assert "// Prompt Program: Math Solver" in result
    assert "function understand_math_problem" in result
    assert "function solve_math_with_cognitive_tools" in result


def test_get_prompt_program_debate():
    """Test that debate prompt program returns correct template."""
    result = get_prompt_program(program_type="debate")

    assert "// Prompt Program: Multi-Perspective Debate" in result
    assert "function frame_debate_question" in result
    assert "function generate_perspective" in result
    assert "function conduct_debate_round" in result
    assert "function synthesize_debate" in result
    assert "function run_multi_perspective_debate" in result


def test_get_prompt_program_unknown():
    """Test that unknown program type returns validation error."""
    result = get_prompt_program(program_type="unknown_type")
    
    assert "Input Validation Error" in result
    assert "program_type" in result


def test_get_molecular_template():
    """Test that molecular template returns the python function string."""
    result = get_molecular_template()

    assert "def create_molecular_context" in result
    assert "Construct a molecular context from examples" in result


def test_resources():
    """Test that resources return expected content."""
    cot = get_cot_molecules()
    assert "# Chain of Thought Templates" in cot
    assert "MOLECULE =" in cot

    layers = get_reference_layers()
    assert "# Context Engineering Layers" in layers
    assert "1. Atoms" in layers
    assert "5. Systems" in layers


def test_get_cell_protocol():
    """Test cell protocol retrieval."""
    from context_engineering_mcp.server import get_cell_protocol

    key_value = get_cell_protocol("cell.protocol.key_value")
    assert "cell.protocol.key_value" in key_value
    assert "new_state" in key_value

    missing = get_cell_protocol("cell.protocol.unknown")
    assert "not found" in missing


def test_thinking_models_tools_render():
    """Ensure thinking model tools register and render expected content without FastMCP."""
    from context_engineering_mcp.cognitive.thinking_models import (
        register_thinking_models,
    )

    class DummyMCP:
        def __init__(self) -> None:
            self.tools: dict[str, object] = {}

        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func

            return decorator

    dummy = DummyMCP()
    register_thinking_models(dummy)

    # Verify all four tools are registered
    assert "understand_question" in dummy.tools
    assert "verify_logic" in dummy.tools
    assert "backtracking" in dummy.tools
    assert "symbolic_abstract" in dummy.tools

    # Test understand_question
    understand = dummy.tools["understand_question"](
        "How do I implement authentication?",
        context="Building a web app",
        constraints="Must be secure",
    )
    assert "/reasoning.understand_question" in understand
    assert "intent_map" in understand
    assert "constraints" in understand
    assert "clarifications" in understand

    # Test verify_logic
    verify = dummy.tools["verify_logic"](
        claim="The system is secure",
        reasoning_trace="Step 1: Added auth. Step 2: Added HTTPS.",
        constraints="Must prevent XSS and CSRF",
    )
    assert "/reasoning.verify_logic" in verify
    assert "premise_check" in verify
    assert "defect_log" in verify
    assert "verdict" in verify

    # Test backtracking
    backtrack = dummy.tools["backtracking"](
        "reach objective", "failed step", trace="trace log", constraints="none"
    )
    assert "/reasoning.backtracking" in backtrack
    assert "recovery_plan" in backtrack

    # Test symbolic_abstract
    symbolic = dummy.tools["symbolic_abstract"](
        "x+1=2", mapping_hint="x->var", goal="solve"
    )
    assert "/symbolic.abstract" in symbolic
    assert "symbol_table" in symbolic


def test_cell_protocol_windowed():
    """Test windowed cell protocol retrieval."""
    from context_engineering_mcp.server import get_cell_protocol

    windowed = get_cell_protocol("cell.protocol.windowed")
    assert "cell.protocol.windowed" in windowed
    assert "max_length" in windowed
    assert "fifo" in windowed.lower() or "recency" in windowed


def test_cell_protocol_episodic():
    """Test episodic cell protocol retrieval."""
    from context_engineering_mcp.server import get_cell_protocol

    episodic = get_cell_protocol("cell.protocol.episodic")
    assert "cell.protocol.episodic" in episodic
    assert "episode" in episodic
    assert "retrieval" in episodic or "log" in episodic


def test_get_organ_debate_council():
    """Test debate_council organ retrieval."""
    result = get_organ("debate_council")

    assert "/organ.debate_council" in result
    assert "multi-perspective" in result.lower() or "debate" in result.lower()
    assert "moderator" in result.lower() or "phase.moderator" in result
    assert "perspectives" in result.lower()
    assert "synthesis" in result.lower()


def test_get_organ_research_synthesis():
    """Test research_synthesis organ retrieval."""
    result = get_organ("research_synthesis")
    
    assert "/organ.research_synthesis" in result
    assert "scout" in result.lower()
    assert "architect" in result.lower()
    assert "scribe" in result.lower()


def test_get_organ_unknown():
    """Test unknown organ returns helpful error with example."""
    result = get_organ("unknown_organ")

    assert "not found" in result.lower()
    assert "debate_council" in result
    assert "/organ.debate_council" in result  # Should include example
