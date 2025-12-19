# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-18

### Added
- **Architect Tool (`design_context_architecture`)**: A new tool that generates system blueprints (Organs + Cells + Models) for building custom agents.
- **Router Logic (`analyze_task_complexity`)**: Updated to support "YOLO Mode" (direct solve) vs "Constructor Mode" (system design).
- **Thinking Models**: 
  - `understand_question`: Decomposes user intent and constraints.
  - `verify_logic`: Audits reasoning traces for fallacies.
  - `backtracking`: Provides error recovery protocols.
  - `symbolic_abstract`: Converts concrete problems to abstract variables.
- **Organs**:
  - `organ.debate_council`: A multi-perspective debate orchestration.
  - `organ.research_synthesis`: A Scout -> Architect -> Scribe workflow.
- **Cells**: Implemented `key_value`, `windowed`, and `episodic` memory protocols.
- **Security**: Added Pydantic validation for all tool inputs to prevent prompt injection.

### Changed
- Refactored project structure into `core`, `systems`, and `cognitive` domains.
- Updated `README.md` and `QUICKSTART.md` for better clarity.

### Security
- Enforced strict input validation using `pydantic`.
