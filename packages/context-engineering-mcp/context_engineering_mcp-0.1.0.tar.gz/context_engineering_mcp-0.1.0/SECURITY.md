# Security & Privacy Policy

## 1. Data Flow Analysis
The **Sutra** MCP server is designed as a **local-first, stateless** utility.

### Architecture
*   **Transport**: Standard Input/Output (Stdio) via the Model Context Protocol (MCP).
*   **Execution**: Local Python process managed by `uv`.
*   **Network**: The server makes **NO** external network requests.
*   **Storage**: The server does **NO** disk I/O for persistence (no databases, no log files).

### Data Lifecycle
1.  **Input**: User data (e.g., task descriptions sent to `analyze_task_complexity`) is received via the secure MCP channel from your client (e.g., Claude Desktop, VS Code).
2.  **Processing**: Data is processed in-memory using simple heuristic logic (string matching).
3.  **Output**: Results are returned immediately to the client.
4.  **Disposal**: All data is discarded immediately after the function returns. No state is retained between calls.

## 2. Privacy Attestation
We formally attest that:
1.  **No Data Exfiltration**: This server does not transmit any data to third-party services, telemetry collectors, or external APIs.
2.  **No Persistence**: This server does not save user inputs or outputs to the file system.
3.  **Local Execution**: All logic runs entirely on your local machine within the `uv` environment.

## 3. Vulnerability Reporting
If you discover a potential security issue, please open an issue in the repository. Since the codebase is small and open, we encourage code review.
