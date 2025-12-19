# Design Strategy: Usability & Optimization for Sutra

## 1. Problem Statement
The `sutra` MCP server provides powerful cognitive architectures, but currently faces two critical friction points:
1.  **High Cognitive Load:** Operators struggle to select the "right" template from a growing library.
2.  **Token Inefficiency:** Using full "Protocol Shells" for simple tasks is overkill, wasting tokens and latency.

## 2. Strategic Paths

### Path A: "The Librarian" (Documentation-as-Tool)
*Concept:* Expose the documentation *to the LLM itself* as a tool.
*   **Mechanism:** A `get_technique_guide(category)` tool.
*   **Workflow:**
    1.  User asks: "How should I solve this?"
    2.  LLM calls: `get_technique_guide("reasoning")`.
    3.  Sutra returns: A summary of available templates (CoT vs Protocol vs Field) with "Best for..." advice.
    4.  LLM selects the appropriate tool.
*   **Pros:** Low implementation cost, high educational value.
*   **Cons:** Adds an extra round-trip (latency).

### Path B: "The Traffic Controller" (Router Pattern)
*Concept:* A lightweight analysis step that directs the prompt to the most efficient path.
*   **Mechanism:** A `analyze_task_complexity(task)` tool.
*   **Workflow:**
    1.  User sends task.
    2.  LLM calls `analyze_task_complexity`.
    3.  Sutra returns: "Complexity: Low. Recommendation: Use standard CoT (Molecule)." OR "Complexity: High. Recommendation: Use Protocol Shell."
*   **Pros:** Optimizes token usage by preventing overkill.
*   **Cons:** Requires the LLM to trust the router's judgment.

### Path C: "Progressive Loading" (Granular Templates)
*Concept:* Break monolithic templates into smaller, composable units.
*   **Mechanism:**
    *   `get_atom(type)`: Tiny, single-shot prompts (Low cost).
    *   `get_molecule(type)`: Few-shot templates (Medium cost).
    *   `get_organ(type)`: Full protocols (High cost).
*   **Workflow:** The LLM starts small and only requests larger structures if the task demands it.
*   **Pros:** Maximum efficiency.
*   **Cons:** Higher complexity for the operator/LLM to assemble pieces.

## 3. Detailed UX Flows

### Flow 1: Manual Discovery ("The Librarian")
*   **User Intent:** "I need a template for X."
*   **Mechanism:** `get_technique_guide(category="all")`
*   **Output:** A structured table of available tools, categorized by:
    *   **Reasoning:** `reasoning.systematic`, `thinking.extended`
    *   **Workflow:** `workflow.test_driven`, `workflow.ui_iteration`
    *   **Code:** `code.analyze`, `code.refactor`
    *   **Project:** `project.explore`, `git.workflow`
*   **Value:** Empowers the user (or LLM) to browse the "menu" before ordering.

### Flow 2: Auto-Dispatch ("The Router")
*   **User Intent:** "Here is a task, just help me do it efficiently."
*   **Mechanism:** `analyze_task_complexity(task_description)`
*   **Logic:**
    *   **Low Complexity:** Suggest `Standard Molecule` (Direct answer).
    *   **Medium Complexity:** Suggest `Prompt Program` (Math, Logic).
    *   **High Complexity:** Suggest `Protocol Shell` (e.g., `reasoning.systematic`).
*   **Output:** A JSON object with `complexity_score`, `recommended_tool`, and `reasoning`.

## 4. Implementation Plan

1.  **Implement `get_technique_guide`:**
    *   Source content from `CLAUDE.md` (which contains the definitive registry).
    *   Format as a Markdown table for easy LLM reading.
2.  **Implement `analyze_task_complexity`:**
    *   A lightweight tool that maps keywords to complexity levels.
3.  **Update `server.py`:**
    *   Add these two new tools.
    *   Populate `get_protocol_shell` with the actual templates found in `CLAUDE.md`.
