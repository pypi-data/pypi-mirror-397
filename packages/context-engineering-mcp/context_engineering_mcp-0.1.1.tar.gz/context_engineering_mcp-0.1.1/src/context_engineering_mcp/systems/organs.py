"""Organ patterns for multi-agent orchestration (Layer 4).

Organs combine programs and cells into cohesive multi-agent workflows.
Based on the architectural spec from .context/00_foundations/04_organs_applications.md
"""

from typing import Final

ORGAN_DEBATE_COUNCIL: Final[str] = """
/organ.debate_council{{
    intent="Generate balanced analysis through multi-perspective debate",

    input={{
        question="<question_or_topic>",
        perspectives=["Optimistic", "Skeptical", "Pragmatic", "Ethical"],
        rounds=2
    }},

    architecture={{
        pattern="moderator → perspectives → debate_rounds → synthesis",
        components=[
            "Moderator Cell: Frames the question and sets debate parameters",
            "Perspective Cells: Each represents a distinct viewpoint",
            "Debate Rounds: Iterative refinement through dialogue",
            "Synthesis Cell: Integrates all perspectives into coherent conclusion"
        ]
    }},

    process=[
        /phase.moderator{{
            role="Frame the debate",
            actions=[
                "Clarify the core question and any ambiguities",
                "Identify key dimensions of debate",
                "Establish evaluation criteria",
                "Set scope and constraints"
            ],
            output="framing_context"
        }},

        /phase.generate_perspectives{{
            role="Generate initial positions",
            for_each="perspective in perspectives",
            actions=[
                "State core position on the question",
                "Provide 2-3 key supporting arguments",
                "Identify underlying assumptions",
                "Acknowledge limitations or counterarguments"
            ],
            output="initial_perspectives[]"
        }},

        /phase.debate_rounds{{
            role="Conduct multi-round debate",
            iterations="rounds",
            for_each_round=[
                "Each perspective responds to strongest counterarguments",
                "Refine or strengthen position based on discussion",
                "Find areas of agreement or common ground",
                "Raise new considerations not yet addressed"
            ],
            output="debate_history[]"
        }},

        /phase.synthesis{{
            role="Synthesize all perspectives",
            actions=[
                "Summarize each major perspective and key arguments",
                "Identify areas of consensus or common ground",
                "Acknowledge irreconcilable differences and why",
                "Provide nuanced conclusion acknowledging complexity",
                "Generate recommendations or implications"
            ],
            output="final_synthesis"
        }}
    ],

    output={{
        framing="Debate framing and context",
        perspectives="All perspective positions",
        debate_rounds="Full debate history",
        synthesis="Integrated multi-perspective conclusion",
        num_perspectives="Count of perspectives considered",
        num_rounds="Number of debate rounds conducted"
    }},

    meta={{
        organ_type="multi_agent_deliberation",
        layer="organs",
        complexity="medium",
        use_cases=[
            "Complex decision analysis",
            "Policy evaluation",
            "Ethical dilemmas",
            "Strategic planning",
            "Research direction setting"
        ]
    }}
}}
"""

ORGAN_RESEARCH_SYNTHESIS: Final[str] = """
/organ.research_synthesis{{
    intent="Conduct comprehensive research and synthesis on a complex topic",

    input={{
        topic="<research_topic>",
        depth="<high|medium|low>",
        format="<report|brief|presentation>"
    }},

    architecture={{
        pattern="scout → architect → scribe",
        components=[
            "Scout Cell: Explores the information landscape and gathers raw data",
            "Architect Cell: Structures the information and outlines the narrative",
            "Scribe Cell: Drafts the final content based on the blueprint"
        ]
    }},

    process=[
        /phase.scout{{
            role="Gather Information",
            actions=[
                "Identify key domains and sub-topics",
                "Retrieve relevant facts and data",
                "Filter for relevance and credibility",
                "Identify gaps requiring further investigation"
            ],
            output="raw_research_data"
        }},

        /phase.architect{{
            role="Structure and Plan",
            actions=[
                "Analyze raw data for patterns and themes",
                "Develop a logical outline or argument structure",
                "Allocate evidence to specific sections",
                "Define tone and style guidelines"
            ],
            output="content_blueprint"
        }},

        /phase.scribe{{
            role="Draft Content",
            actions=[
                "Expand blueprint into full prose",
                "Integrate evidence seamlessly",
                "Refine language for clarity and impact",
                "Format according to requirements"
            ],
            output="final_draft"
        }}
    ],

    output={{
        research_summary="Overview of gathered data",
        blueprint="Structural plan of the content",
        final_document="The complete synthesized output"
    }},

    meta={{
        organ_type="sequential_workflow",
        layer="organs",
        complexity="medium",
        use_cases=[
            "Deep dive research reports",
            "Literature reviews",
            "Technical documentation",
            "Content creation from disparate sources"
        ]
    }}
}}
"""

ORGAN_TOOL_MASTER: Final[str] = """
/organ.tool_master{{
    intent="Act as a specialized Supervisor Agent that manages tool selection, execution, and output compression.",

    input={{
        intent="<high_level_goal>",
        task_type="<architect|research|reasoning|code>",
        constraints="<optional_constraints>",
        output_format="<concise|full>"
    }},

    architecture={{
        pattern="router → executor → distiller",
        components=[
            "Registry Cache (Cell): A learned mapping of intents to tool definitions (optimizes discovery).",
            "Router (Phase): Selects the optimal tool using the Registry or heuristic analysis.",
            "Executor (Phase): Constructs valid API calls and handles retries.",
            "Distiller (Phase): Compresses verbose tool outputs into high-signal summaries."
        ]
    }},

    process=[
        /phase.router{{
            role="Select Tool",
            actions=[
                "Check Registry Cache for known intent->tool mappings",
                "If unknown, analyze intent using 'analyze_task_complexity'",
                "Select tool: 'design_context_architecture' (System Building)",
                "Select tool: 'get_technique_guide' (Discovery)",
                "Select tool: 'reasoning.*' (Logic/Cognition)"
            ],
            output="selected_tool_spec"
        }},

        /phase.executor{{
            role="Execute Tool",
            actions=[
                "Construct valid JSON arguments based on selected tool schema",
                "Execute tool call",
                "Handle validation errors (max 1 retry)"
            ],
            output="raw_tool_output"
        }},

        /phase.distiller{{
            role="Optimize Signal",
            actions=[
                "If output_format='concise': Apply lossy summarization (remove boilerplate, keep data)",
                "If output_format='full': Pass through raw output",
                "Extract core artifacts (e.g., code blocks, protocol strings)",
                "Log full details to episodic memory (offloading)"
            ],
            output="high_signal_result"
        }}
    ],

    output={{
        tool_used="Name of tool executed",
        artifact="The optimized result",
        token_savings="Estimate of tokens saved via distillation",
        cache_update="New intent->tool mapping to store"
    }},

    meta={{
        organ_type="supervisor_utility",
        layer="organs",
        complexity="low",
        use_cases=[
            "Delegating complex tool chains",
            "Reducing context pollution in long conversations",
            "Abstracting API changes from client agents"
        ]
    }}
}}
"""


def get_organ_template(organ_name: str) -> str:
    """Return an organ template for orchestrating multi-agent workflows.

    Args:
        organ_name: Identifier for the organ (e.g., "debate_council").

    Returns:
        Template string for the requested organ, or error message if not found.
    """
    normalized_name = (
        organ_name.lower().replace("organ.", "").replace("_", "").replace("-", "")
    )

    # Match debate_council variants
    if normalized_name in ["debatecouncil", "debate", "multiperspective"]:
        return ORGAN_DEBATE_COUNCIL

    # Match research_synthesis variants
    if normalized_name in ["researchsynthesis", "research", "scoutarchitectscribe"]:
        return ORGAN_RESEARCH_SYNTHESIS

    # Match tool_master variants
    if normalized_name in ["toolmaster", "tool", "master", "meta"]:
        return ORGAN_TOOL_MASTER

    # Return helpful error for unknown organs
    available = ["debate_council", "research_synthesis", "tool_master"]
    return (
        f"// Organ '{organ_name}' not found.\\n"
        f"// Available organs: {', '.join(available)}\\n"
        f"// Returning debate_council as example:\\n\\n" + ORGAN_DEBATE_COUNCIL
    )


__all__ = [
    "ORGAN_DEBATE_COUNCIL",
    "ORGAN_RESEARCH_SYNTHESIS",
    "ORGAN_TOOL_MASTER",
    "get_organ_template",
]
