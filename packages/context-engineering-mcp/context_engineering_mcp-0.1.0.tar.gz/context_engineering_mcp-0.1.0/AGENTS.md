# AGENTS.md: The Sutra Contribution Protocol

> "The limit of your context is the limit of your world."

## 1. Mission Statement

You are entering **Sutra**, a Model Context Protocol (MCP) server dedicated to the science of **Context Engineering**. Your goal is not merely to write Python code, but to architect the "Operating System" for meaning, reasoning, and memory in Large Language Models.

We build primitives that allow agents to:

1. **Reason** (Cognitive Tools/Thinking Models)
2. **Remember** (Memory Cells/State)
3. **Collaborate** (Organs/Multi-agent Systems)
4. **Resonate** (Neural Fields/Continuous Semantics)

## 2. The Context Stack (Architecture)

All contributions must map to a specific layer of the Context Engineering Foundation. Do not introduce flat logic where structured context is required.

* **Layer 0: Atoms (`/core/atoms.py`)**: Raw instruction prompts.
* **Layer 1: Molecules (`/core/molecules.py`)**: Few-shot templates and CoT patterns.
* **Layer 2: Cells (`/core/cells.py`)**: Stateful memory protocols (JSON schemas + system prompts).
* **Layer 3: Organs (`/systems/organs.py`)**: Multi-agent orchestration blueprints.
* **Layer 4: Fields (`/systems/fields.py`)**: Mathematical models of semantic resonance and decay.
* **Layer 5: Cognitive (`/cognitive/`)**: Reasoning engines (IBM Tools, Symbolic Mechanisms).

## 3. Coding Standards (The Implementation)

* **Language**: Python 3.10+
* **Framework**: `mcp` (Model Context Protocol).
* **Style**:
  * **Type Hinting**: Mandatory. Use `typing` heavily.
  * **Docstrings**: Google Style. Every prompt template must explain *why* it works based on foundation modules.
  * **Modularity**: One tool/resource per function. Do not create god-objects.

## 4. The Journaling Protocol

Memory is critical. You must maintain the **Context Ledger**.

* **File**: `.journal.md`
* **Trigger**: After every significant logical unit (feature complete, bug fix, refactor).
* **Format**:

    ```markdown
    ## [YYYY-MM-DD HH:MM] Feature Name
    - **Intent**: What did we try to build?
    - **Changes**: What files were touched?
    - **Reasoning**: Why this approach? (Cite Module X)
    - **State**: [Success/WIP/Failed]
    ```

## 5. Interaction Mode

When working in this repo:

* **Read First**: Always ingest `TODO.md` and the relevant `src/` files before generating code.
* **Verify**: Before committing, ask: "Does this prompt template enforce structured output?"
* **Reflect**: If a feature feels "flat" (just text), ask how to add "dimension" (state, structure, or math).
