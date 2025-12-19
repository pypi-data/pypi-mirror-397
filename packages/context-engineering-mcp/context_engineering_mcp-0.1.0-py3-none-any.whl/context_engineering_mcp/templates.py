"""Legacy template exports.

This module preserves the previous flat import surface while delegating storage
to the domain-driven core modules.
"""

from context_engineering_mcp.core.atoms import PROTOCOL_SHELL_STRUCTURE
from context_engineering_mcp.core.molecules import (
    CODE_ANALYZE,
    MOLECULAR_CONTEXT_FUNC,
    PROJECT_EXPLORE,
    PROTOCOL_REGISTRY,
    REASONING_SYSTEMATIC,
    THINKING_EXTENDED,
    WORKFLOW_TDD,
    get_protocol_template,
)
from context_engineering_mcp.core.programs import PROMPT_PROGRAM_MATH_TEMPLATE

__all__ = [
    "PROTOCOL_SHELL_STRUCTURE",
    "MOLECULAR_CONTEXT_FUNC",
    "REASONING_SYSTEMATIC",
    "THINKING_EXTENDED",
    "WORKFLOW_TDD",
    "CODE_ANALYZE",
    "PROJECT_EXPLORE",
    "PROTOCOL_REGISTRY",
    "PROMPT_PROGRAM_MATH_TEMPLATE",
    "get_protocol_template",
]
