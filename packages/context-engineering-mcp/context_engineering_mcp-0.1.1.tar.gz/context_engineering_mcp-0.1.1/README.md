# Sutra

mcp-name: io.github.4rgon4ut/sutra

**The MCP Context Engineering Engine**

Sutra is a Model Context Protocol (MCP) server that transforms how LLMs handle reasoning, memory, and orchestration. It provides a "Standard Library" of cognitive tools (Thinking Models), memory structures (Cells), and multi-agent patterns (Organs).

## Installation

### Using `uv` (Recommended)
```bash
uv tool install context-engineering-mcp
```

### Using `pip`
```bash
pip install context-engineering-mcp
```

## Configuration

Select your agent below and copy-paste the config.

<details>
<summary>Claude Desktop</summary>

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "sutra": {
      "command": "uv",
      "args": ["tool", "run", "context-engineering-mcp"]
    }
  }
}
```
</details>

<details>
<summary>Claude Code</summary>

Run this in your terminal:
```bash
claude mcp add sutra uv tool run context-engineering-mcp
```
</details>

<details>
<summary>Aider</summary>

Run aider with the mcp flag:
```bash
aider --mcp "uv tool run context-engineering-mcp"
```
Or add to `.aider.conf.yml`:
```yaml
mcp: ["uv tool run context-engineering-mcp"]
```
</details>

<details>
<summary>Gemini CLI</summary>

Add to `~/.gemini/settings.json`:
```json
{
  "mcpServers": {
    "sutra": {
      "command": "uv",
      "args": ["tool", "run", "context-engineering-mcp"]
    }
  }
}
```
</details>

<details>
<summary>Cursor / Windsurf</summary>

In MCP settings, add a new server:
- **Name**: Sutra
- **Type**: command
- **Command**: `uv tool run context-engineering-mcp`
</details>

<details>
<summary>Codex</summary>

Add to your config (TOML):
```toml
[mcp_servers.sutra]
command = "uv"
args = ["tool", "run", "context-engineering-mcp"]
```
</details>

## Core Features (v0.1.0)

### 1. The Gateway (Router)
Sutra automatically analyzes your request to decide the best strategy:
- **YOLO Mode**: For immediate tasks ("Fix this bug"), it routes to specific cognitive tools.
- **Constructor Mode**: For system design ("Build a bot"), it routes to the Architect.

### 2. The Architect
Generates blueprints for custom agents, combining:
- **Thinking Models**: `understand_question`, `verify_logic`, `backtracking`, `symbolic_abstract`.
- **Memory Cells**: `key_value` (State), `windowed` (Short-term), `episodic` (Long-term).
- **Organs**: `debate_council` (Multi-perspective), `research_synthesis` (Deep Dive).

### 3. The Librarian
A manual discovery tool (`get_technique_guide`) that lets you or the agent browse the full catalog of Context Engineering techniques.

## Development

**Requirements**: Python 3.10+, `uv` (optional but recommended).

1. Clone the repo:
   ```bash
   git clone https://github.com/4rgon4ut/sutra.git
   cd sutra
   ```
2. Install dependencies:
   ```bash
   uv sync --all-extras
   # OR
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## License
MIT