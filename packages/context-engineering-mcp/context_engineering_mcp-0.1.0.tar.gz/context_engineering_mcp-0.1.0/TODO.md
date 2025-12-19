# Sutra Roadmap: From Library to Engine

**Current Status**: `v0.1.0` (Feature Complete, Secure, Polished)
**Target Status**: `v0.2.0` (Dynamic Context Orchestration)

---

## Phase 1: The Cognitive Foundry (Thinking Models)
- [x] **Refactor Directory Structure**
- [x] **Implement `cognitive/thinking_models.py`**
    - [x] `understand_question`
    - [x] `backtracking`
    - [x] `symbolic_abstract`
    - [x] `verify_logic`
- [x] **Implement Prompt Program Generator (`core/programs.py`)**
    - [x] `math` program type.
    - [x] `debate` program type.

## Phase 2: The Cell Laboratory (Memory & State)
- [x] **Implement `core/cells.py`**
    - [x] `cell.protocol.key_value`
    - [x] `cell.protocol.windowed`
    - [x] `cell.protocol.episodic`

## Phase 3: The Organ Assembly (Orchestration)
- [x] **Implement `systems/organs.py`**
    - [x] `organ.research_synthesis` (Scout -> Architect -> Scribe)
    - [x] `organ.debate_council`

## Phase 4: Maintenance & Quality
- [x] **Add Schema Validators**
    - [x] Pydantic models for all Tool inputs.
- [x] **Testing & Linting**
    - [x] 100% test pass rate.
    - [x] Ruff linting clean.
- [ ] **Documentation**
    - [ ] Auto-generate API reference.

## Phase 5: v0.2.0 Prospects
- [ ] **Serena/Indexing Integration**
    - Reintroduce optional Serena indexing to keep abstraction graph and prefs accessible.
- [ ] **Dynamic Orchestration**
    - Agents that can self-select and chain these tools.
