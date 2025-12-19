"""Layer 2: Cells (stateful memory prompt protocols).

These templates encode persistent context behaviors (key-value, windowed,
episodic) at the prompt level, enabling external callers to enforce state
management without embedding storage logic here.
"""

from typing import Dict, Final, Optional

CELL_PROTOCOL_KEY_VALUE: Final[str] = """
/cell.protocol.key_value{
    intent="Maintain a persistent key-value store with explicit state updates",
    input={
        current_state="<json_object>",
        key="<key>",
        value="<value>",
        operation="<set|get|delete>",
        constraints="<constraints_or_schema>"
    },
    process=[
        /validate{action="Ensure value respects constraints/schema"},
        /update{action="Apply the operation to the state map"},
        /summarize{action="Summarize changes for downstream context"}
    ],
    output={
        new_state="<json_object>",
        delta="Description of modifications",
        rationale="Why this change was applied"
    }
}
"""

CELL_PROTOCOL_WINDOWED: Final[str] = """
/cell.protocol.windowed{
    intent="Maintain a sliding context window with eviction policy",
    input={
        window="<list_of_messages_or_events>",
        new_event="<incoming_event>",
        max_length="<int>",
        policy="<fifo|recency|salience>"
    },
    process=[
        /ingest{action="Append or merge the new event"},
        /evict{action="Remove items per policy to respect max_length"},
        /compress{action="Optionally summarize evicted content"}
    ],
    output={
        updated_window="<list_after_eviction>",
        summary="Optional compression of evicted items",
        justification="Policy reasoning for evictions"
    }
}
"""

CELL_PROTOCOL_EPISODIC: Final[str] = """
/cell.protocol.episodic{
    intent="Write-only episodic log for long-horizon recall",
    input={
        episode_id="<string>",
        event="<event_or_message>",
        tags="<list_of_tags>",
        importance="<low|medium|high>"
    },
    process=[
        /record{action="Append event with timestamp and tags"},
        /index{action="Generate retrieval cues (keywords, embeddings)"},
        /checkpoint{action="Emit snapshot pointers for later recall"}
    ],
    output={
        log_entry="Structured record appended",
        retrieval_keys="Cues for future lookup",
        checkpoint_ref="Pointer to episode boundary"
    }
}
"""

CELL_PROTOCOL_REGISTRY: Final[Dict[str, str]] = {
    "cell.protocol.key_value": CELL_PROTOCOL_KEY_VALUE,
    "cell.protocol.windowed": CELL_PROTOCOL_WINDOWED,
    "cell.protocol.episodic": CELL_PROTOCOL_EPISODIC,
}


def get_cell_protocol_template(name: str) -> Optional[str]:
    """Return a cell protocol template by identifier.

    Args:
        name: Protocol key such as 'cell.protocol.key_value'.

    Returns:
        The corresponding template string if registered.
    """
    return CELL_PROTOCOL_REGISTRY.get(name)


__all__ = [
    "CELL_PROTOCOL_KEY_VALUE",
    "CELL_PROTOCOL_WINDOWED",
    "CELL_PROTOCOL_EPISODIC",
    "CELL_PROTOCOL_REGISTRY",
    "get_cell_protocol_template",
]
