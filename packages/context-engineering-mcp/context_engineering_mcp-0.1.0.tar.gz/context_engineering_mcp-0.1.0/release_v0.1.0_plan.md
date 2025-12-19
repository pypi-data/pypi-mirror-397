# Sutra v0.1.0 Release Plan

## Thinking Model: `understand_question` (Emulated)

```
/reasoning.understand_question{
    intent="Clarify the ask before solving by isolating intent, constraints, and required outputs",
    input={
        question="Scope out what will be a good threshold for sutra v0.1.0 release. Consider good practices for OSS. Check features (implemented/planned). I want 0.1.0 to be: Feature complete, Polished, Secure",
        context="Current State: Cognitive tools, Cells, Molecules implemented. Missing Pydantic validators. Basic testing exists.",
        constraints="OSS Best Practices, Feature Complete (understandable flow), Polished (no bugs, tests), Secure (no prompt injection)"
    },
    process=[
        /intent_map{action="Prepare codebase for public v0.1.0 release ensuring quality, security, and usability"},
        /constraints{action="Must have robust input validation (Pydantic). Must have comprehensive tests. Must be documented."},
        /decomposition{action="1. Security: Pydantic Validators. 2. Polish: Linting & Tests. 3. Features: Documentation & Flow check."},
        /risk_check{action="Prompt injection is the main security risk. Lack of types on inputs is a stability risk."}
    ],
    output={
        intent="Release Sutra v0.1.0 as a secure, polished, and usable MCP server.",
        constraints="Pydantic Validation, 100% Test Pass Rate, Clear Docstrings, No Format String Vulnerabilities",
        clarifications="Are there specific Organs needed for v0.1.0? (Assuming Debate Council is sufficient)",
        proposed_plan="See Detailed Roadmap below."
    }
}
```

## Detailed Roadmap (Validation Loop)

For each feature/fix, we apply the following loop:
1.  **Rationalize:** Identify the need (Security/Polish/Feature).
2.  **Implement:** Code the change.
3.  **Validate:** Run `pytest`, `ruff`, and manual verification.
4.  **Commit:** Linux-kernel style message.

### Phase 1: Security & Robustness (Priority: High)
*   **Goal:** Mitigate prompt injection and runtime errors.
*   **Action:** Replace raw `str` type hints with Pydantic `BaseModel` schemas for all tool inputs.
*   **Rationale:** `str.format()` is vulnerable. Pydantic ensures structure and can validate content before injection.

### Phase 2: Polish & Testing (Priority: Medium)
*   **Goal:** "No crap and thrash".
*   **Action:**
    *   Run `ruff` on the entire codebase and fix all linter errors.
    *   Ensure `pytest` passes all tests. Add tests for new Pydantic models.
*   **Rationale:** A polished release must be clean and reliable.

### Phase 3: Usability & Flow (Priority: Medium)
*   **Goal:** "Understandable for LLMs".
*   **Action:** Review and refine tool docstrings in `server.py` and `thinking_models.py`.
*   **Rationale:** The LLM uses the docstrings to understand how to use the tools. Clear, concise instructions are vital.

### Phase 4: Final Review
*   **Goal:** Verify readiness.
*   **Action:** Manual walkthrough of the "Context Engineering" flow using the `sutra` tools.
