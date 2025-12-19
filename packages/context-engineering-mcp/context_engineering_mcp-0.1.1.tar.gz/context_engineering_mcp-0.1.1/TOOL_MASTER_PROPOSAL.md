# Proposal: The Universal Tool-Master Organ

## 1. Problem Statement
Agents currently suffer from "Tool Amnesia." Every new session requires them to re-discover how to use available MCP tools (e.g., FileSystem, Git, Brave Search). This leads to:
- **Wasted Tokens**: Re-reading schemas and error logs.
- **Context Pollution**: Filling the window with verbose API definitions.
- **Missed Synergies**: Agents failing to combine tools (e.g., "Search" + "Write") effectively.

## 2. Solution: The Tool-Master Organ
A **Meta-Orchestration Layer** that sits between the User/Agent and the raw MCP Tools. It acts as a "Driver" that knows how to operate the machinery.

### Core Philosophy
**"Research once, Execute efficiently."**

## 3. Architecture

We propose a **4-Cell, 5-Phase** architecture:

### Components (The Machinery)
1.  **Registry Cell (Episodic Memory)**:
    - Stores "Learned Patterns": `{"git_commit": "Requires -m flag and staged files"}`.
    - Stores "Synergies": `{"research_task": ["search_tool", "read_page_tool", "file_writer"]}`.
2.  **Scout Cell (The Eye)**:
    - Responsible for scanning the `list_tools` output.
    - Detects *new* or *unknown* MCP servers.
3.  **Architect Cell (The Brain)**:
    - Maps the User's Intent -> Tool Chain.
    - e.g., "User wants to fix a bug" -> `[grep_error, read_file, patch_file, run_test]`.
4.  **Distiller Cell (The Filter)**:
    - Compresses verbose JSON outputs into high-signal summaries.

### Process Flow (The Protocol)

#### Phase 1: Discovery (The Scout)
- **Action**: Inspects the current environment's tool list.
- **Logic**: "Do I recognize these tools?"
    - *If Yes*: Load cached usage patterns from Registry.
    - *If No*: Trigger "Investigation Mode" (inspect schema, look for `help` tools).

#### Phase 2: Synergy Mapping (The Architect)
- **Action**: Cross-reference User Intent with Available Tools.
- **Logic**: Identify chains.
    - *Example*: "I have `search` and `filesystem`. I can do 'Research & Save'."
    - *Example*: "I have `interpreter` and `csv_reader`. I can do 'Data Analysis'."

#### Phase 3: Execution (The Hand)
- **Action**: Execute the tool chain.
- **Robustness**: If a tool fails (Schema Validation Error), the Organ *self-corrects* using the error message without bothering the user.

#### Phase 4: Distillation (The Scribe)
- **Action**: Parse the raw output.
- **Logic**: Remove ID fields, timestamps, and boilerplate. Keep the *Content*.
- **Output**: A clean, markdown-formatted result.

## 4. Usage Patterns

### A. The "Cold Start" (New Environment)
*User*: "Please fix the bug in main.py."
*Tool-Master*:
1.  Scans tools. Sees `edit_file`, `run_shell`.
2.  Recognizes `run_shell`. Checks schema.
3.  Plans: `run_shell(pytest)` -> `read_file(main.py)` -> `edit_file(fix)`.
4.  Executes.
5.  Returns: "Fixed bug. Tests passed." (Hides the 40 lines of JSON).

### B. The "Power User" (Complex Delegation)
*User*: "Research the latest MCP updates and summarize."
*Tool-Master*:
1.  Scans tools. Sees `brave_search`.
2.  Plans: `brave_search("MCP updates")` -> `read_page(url)` -> `summarize`.
3.  Distills: Returns a clean bulleted list.

## 5. Implementation Strategy
We will implement this as `organ.tool_master` in `src/context_engineering_mcp/systems/organs.py`.

**Key Features to Build:**
1.  **Dynamic Introspection Prompt**: Instructions for the LLM to look at its *own* tool definition list.
2.  **Pattern Library**: A small few-shot library of common tool patterns (Git, FileSystem, Search) injected into the Registry Cell.
3.  **Error Recovery Loop**: A specific sub-routine for handling `ToolExecutionError`.

---

**Approval Required**:
Shall we proceed with implementing this `organ.tool_master`?
