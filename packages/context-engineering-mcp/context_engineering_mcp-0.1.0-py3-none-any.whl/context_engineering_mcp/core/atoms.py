"""Layer 0: Atoms.

This module contains base prompt shells used to scaffold higher-level protocols.
"""

from typing import Final

PROTOCOL_SHELL_STRUCTURE: Final[str] = """
/protocol.{name}{{
    intent="{intent}",
    input={{
        param1="value1",
        param2="value2"
    }},
    process=[
        /step1{{action="do something"}},
        /step2{{action="do something else"}}
    ],
    output={{
        result1="expected output 1",
        result2="expected output 2"
    }}
}}
"""


def format_protocol_shell(name: str, intent: str) -> str:
    """Render a protocol shell with the provided name and intent.

    Args:
        name: Protocol identifier to append to `/protocol`.
        intent: Purpose statement describing the protocol's goal.

    Returns:
        Formatted protocol shell with placeholder input/output sections.
    """
    return PROTOCOL_SHELL_STRUCTURE.format(name=name, intent=intent)


__all__ = ["PROTOCOL_SHELL_STRUCTURE", "format_protocol_shell"]
