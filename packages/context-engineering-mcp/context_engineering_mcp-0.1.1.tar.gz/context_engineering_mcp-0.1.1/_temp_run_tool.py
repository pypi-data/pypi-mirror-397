import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

from context_engineering_mcp.server import design_context_architecture, get_protocol_shell

goal = "Research and build a Tool-Master Organ that abstracts MCP tool usage and documentation for other agents."
constraints = "Research first, then build. Must save tokens and context. Abstraction layer for tools."

# 1. Get Architecture Blueprint
blueprint = design_context_architecture(goal=goal, constraints=constraints)
print("--- BLUEPRINT ---")
print(blueprint)

# 2. Get Protocol Shell (Custom Intent)
intent = "Research existing tool usage patterns and build a Tool-Master Organ to optimize token usage and abstraction."
shell = get_protocol_shell(name="organ.tool_master", intent=intent)
print("\n--- SHELL ---")
print(shell)
