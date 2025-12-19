# Code Scalpel

[![PyPI version](https://badge.fury.io/py/code-scalpel.svg)](https://pypi.org/project/code-scalpel/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-4033%20passed-brightgreen.svg)](https://github.com/tescolopio/code-scalpel)
[![Coverage](https://img.shields.io/badge/coverage-94.86%25-brightgreen.svg)](release_artifacts/v3.0.0/)

**MCP Server Toolkit for AI Agents - v3.0.0 "Autonomy"**

Code Scalpel enables AI assistants (Claude, GitHub Copilot, Cursor) to perform surgical code operations without hallucination. Extract exactly what's needed, modify without collateral damage, verify before applying.

## Installation

```bash
pip install code-scalpel
```

Or with [uv](https://docs.astral.sh/uv/) (recommended for MCP):
```bash
uvx code-scalpel --help
```

---

## Quick Start by Server Type

Code Scalpel supports multiple transport methods. Choose based on your use case:

| Transport | Best For | Command |
|-----------|----------|---------|
| **stdio** | Claude Desktop, VS Code, Cursor | `uvx code-scalpel mcp` |
| **HTTP** | Remote access, team servers | `code-scalpel mcp --http --port 8593` |
| **Docker** | Isolated environments, CI/CD | `docker run -p 8593:8593 code-scalpel` |

### Option 1: VS Code / GitHub Copilot (stdio)

Create `.vscode/mcp.json` in your project:

```json
{
  "servers": {
    "code-scalpel": {
      "type": "stdio",
      "command": "uvx",
      "args": ["code-scalpel", "mcp", "--root", "${workspaceFolder}"]
    }
  }
}
```

Then in VS Code: `Ctrl+Shift+P` → "MCP: List Servers" → Start code-scalpel

### Option 2: Claude Desktop (stdio)

Add to `claude_desktop_config.json`:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp", "--root", "C:\\Projects\\myapp"]
    }
  }
}
```

### Option 3: HTTP Server (Remote/Team)

```bash
# Start HTTP server on port 8593
code-scalpel mcp --http --port 8593

# With LAN access for team
code-scalpel mcp --http --port 8593 --allow-lan

# Health check endpoint (port 8594)
curl http://localhost:8594/health
```

Connect from VS Code:
```json
{
  "servers": {
    "code-scalpel": {
      "type": "http",
      "url": "http://localhost:8593/mcp"
    }
  }
}
```

### Option 4: Docker (Isolated/CI)

```bash
# Run with project mounted
docker run -d \
  --name code-scalpel \
  -p 8593:8593 \
  -p 8594:8594 \
  -v /path/to/project:/project \
  ghcr.io/tescolopio/code-scalpel:3.0.0

# Verify health
curl http://localhost:8594/health
# {"status":"healthy","version":"3.0.0","tools":19}

# Connect via HTTP transport
```

**Docker Compose:**
```yaml
services:
  code-scalpel:
    image: ghcr.io/tescolopio/code-scalpel:3.0.0
    ports:
      - "8593:8593"
      - "8594:8594"
    volumes:
      - ./:/project
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8594/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Option 5: Cursor IDE

Add to Cursor settings (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp"]
    }
  }
}
```

---

> **v3.0.0 "AUTONOMY" RELEASE** (December 18, 2025)  
> Comprehensive Coverage, Stability, and Autonomy Foundation
>
> | Component | Status | Notes |
> |-----------|--------|-------|
> | Languages | **4** | Python, TypeScript, JavaScript, Java |
> | Security Scanning | **17+ types** | SQL, XSS, NoSQL, LDAP, DOM XSS, Prototype Pollution |
> | Cross-File Analysis | **STABLE** | Import resolution, taint tracking, extraction |
> | MCP Protocol | **COMPLETE** | Health endpoint, Progress tokens, Roots capability |
> | Token Efficiency | **99%** | Surgical extraction vs full file |
> | Performance | **25,000+ LOC/sec** | Project-wide analysis |
> | MCP Tools | **19 tools** | analyze, extract, security, test-gen, cross-file, policy |
> | Test Suite | **4,033 tests** | 94.86% combined coverage |
>
> See [RELEASE_NOTES_v3.0.0.md](docs/release_notes/RELEASE_NOTES_v3.0.0.md) for full details.

---

## The Revolution: Code as Graph, Not Text

Most AI coding tools treat your codebase like a book—they "read" as much as possible to understand context. This hits a hard ceiling: the **Context Window**.

**Code Scalpel changes the game.** It stops treating code as "text" and starts treating it as a **graph**—a deterministic pre-processor for probabilistic models.

### Breaking the Context Window Tyranny

| The Old Way (RAG/Chat) | The Code Scalpel Way |
|------------------------|----------------------|
| "Here are all 50 files. Good luck." | "Here's the variable definition, 3 callers, and 1 test. Nothing else." |
| Retrieve similar text chunks (fuzzy) | Trace variable dependencies (precise) |
| Context limit is a hard wall | Context limit is irrelevant—we slice to fit |
| "I think this fixes it" | "I have mathematically verified this path" |

### Why This Matters

**1. Operate on Million-Line Codebases with 4K Token Models**

Instead of stuffing files into context, Code Scalpel's **Program Dependence Graph (PDG)** surgically extracts *only* the code that matters:

```
User: "Refactor the calculate_tax function"
Old Way: Send 10 files (15,000 tokens) → Model confused
Scalpel: Send function + 3 dependencies (200 tokens) → Precise fix
```

**2. Turn "Dumb" Local LLMs into Geniuses**

Local models (Llama, Mistral) are fast and private but struggle with complex reasoning. Code Scalpel offloads the thinking:

- **Before:** "Does path A allow null?" → Model guesses
- **After:** Symbolic Engine proves it → Model receives fact: "Path A impossible. Path B crashes."

A 7B model + Code Scalpel outperforms a 70B model flying blind.

**3. From Chatbot to Operator (OODA Loop)**

Code Scalpel transforms LLMs from "suggestion machines" into autonomous operators:

1. **Observe:** `analyze_code` → Map the structure
2. **Orient:** `extract_code` → Isolate the bug's ecosystem  
3. **Decide:** `symbolic_execute` → Verify fix mathematically
4. **Act:** `update_symbol` → Apply without breaking syntax

---

## Quick Comparison

| Feature | Traditional Tools | Code Scalpel |
|---------|------------------|--------------|
| Pattern matching (regex) | [COMPLETE] | **Taint tracking** through variables |
| Single file analysis | [COMPLETE] | **Cross-file** dependency graphs |
| Manual test writing | [COMPLETE] | **Z3-powered** test generation |
| Generic output | [COMPLETE] | **AI-optimized** structured responses |
| Context strategy | Stuff everything | **Surgical slicing** |

---

## Quick Demo

### 1. Security: Find Hidden Vulnerabilities

```python
# The SQL injection is hidden through 3 variable assignments
# Regex linters miss this. Code Scalpel doesn't.

code-scalpel scan demos/vibe_check.py
# → SQL Injection (CWE-89) detected at line 38
#   Taint path: request.args → user_id → query_base → final_query
```

### 2. Secret Scanning: Detect Hardcoded Secrets

```python
# Detects AWS Keys, Stripe Secrets, Private Keys, and more
# Handles bytes, f-strings, and variable assignments

code-scalpel scan demos/config.py
# → Hardcoded Secret (AWS Access Key) detected at line 12
# → Hardcoded Secret (Stripe Secret Key) detected at line 45
```

### 3. Analysis: Understand Complex Code

```python
from code_scalpel import CodeAnalyzer

analyzer = CodeAnalyzer()
result = analyzer.analyze("""
def loan_approval(income, debt, credit_score):
    if credit_score < 600:
        return "REJECT"
    if income > 100000 and debt < 5000:
        return "INSTANT_APPROVE"
    return "STANDARD"
""")

print(f"Functions: {result.metrics.num_functions}")
print(f"Complexity: {result.metrics.cyclomatic_complexity}")
```

### 4. Test Generation: Cover Every Path

```bash
# Z3 solver derives exact inputs for all branches
code-scalpel analyze demos/test_gen_scenario.py

# Generates:
# - test_reject: credit_score=599
# - test_instant_approve: income=100001, debt=4999, credit_score=700
# - test_standard: income=50000, debt=20000, credit_score=700
```

## MCP Tools Reference (19 Total)

**Core Tools (v1.0.0)**
| Tool | Description |
|------|-------------|
| `analyze_code` | Parse structure, extract functions/classes/imports |
| `security_scan` | Detect SQLi, XSS, command injection via taint analysis |
| `symbolic_execute` | Explore all execution paths with Z3 |
| `generate_unit_tests` | Create pytest/unittest from symbolic paths |
| `simulate_refactor` | Verify changes are safe before applying |
| `extract_code` | Surgically extract functions/classes with dependencies |
| `update_symbol` | Safely replace functions/classes in files |
| `crawl_project` | Discover project structure and file analysis |

**Context Tools (v1.5.0)**
| Tool | Description |
|------|-------------|
| `get_file_context` | Retrieve surrounding code for specific locations |
| `get_symbol_references` | Find all usages of a symbol across project |
| `get_call_graph` | Generate call graphs and trace execution flow |
| `get_project_map` | Build complete project map and entry points |
| `scan_dependencies` | Scan for vulnerable dependencies (OSV API) |

**Cross-File Tools (v1.5.1)**
| Tool | Description |
|------|-------------|
| `get_cross_file_dependencies` | Build import graphs and resolve symbols |
| `cross_file_security_scan` | Detect vulnerabilities spanning modules |

**v2.5.0+ Tools**
| Tool | Description |
|------|-------------|
| `unified_sink_detect` | Unified polyglot sink detection with confidence |
| `get_graph_neighborhood` | Extract k-hop subgraph around a node |
| `validate_paths` | Validate path accessibility for Docker |
| `verify_policy_integrity` | Cryptographic policy file verification |

## Features

### Polyglot Analysis
- **Python**: Full AST + PDG + Symbolic Execution
- **JavaScript**: Tree-sitter parsing + IR normalization
- **Java**: Enterprise-ready cross-file analysis

### Security Analysis
- SQL Injection (CWE-89)
- Cross-Site Scripting (CWE-79) - Flask/Django sinks
- Command Injection (CWE-78)
- Path Traversal (CWE-22)
- Code Injection (CWE-94) - eval/exec
- Insecure Deserialization (CWE-502) - pickle
- SSRF (CWE-918)
- Weak Cryptography (CWE-327) - MD5/SHA1
- Hardcoded Secrets (CWE-798) - 30+ patterns (AWS, GitHub, Stripe, private keys)
- NoSQL Injection (CWE-943) - MongoDB PyMongo/Motor
- LDAP Injection (CWE-90) - python-ldap/ldap3

### Performance
- **200x cache speedup** for unchanged files
- **5-second Z3 timeout** prevents hangs
- Content-addressable caching with version invalidation

## CLI Reference

```bash
# Analyze code structure
code-scalpel analyze app.py
code-scalpel analyze src/ --json

# Security scan
code-scalpel scan app.py
code-scalpel scan --code "cursor.execute(user_input)"

# Start MCP server
code-scalpel mcp                              # stdio (Claude Desktop)
code-scalpel mcp --http --port 8593           # HTTP (network)
code-scalpel mcp --root /project --allow-lan  # Team deployment
```

## Docker Deployment

```bash
# Build
docker build -t code-scalpel .

# Run MCP server
docker run -p 8593:8593 -v $(pwd):/app/code code-scalpel

# Connect at http://localhost:8593/mcp
```

## Documentation

**v3.0.0 Release Documentation:**
- [docs/MIGRATION_v2.5_to_v3.0.md](docs/MIGRATION_v2.5_to_v3.0.md) - Upgrade guide from v2.5.0 (no breaking changes)
- [docs/API_CHANGES_v3.0.0.md](docs/API_CHANGES_v3.0.0.md) - Complete API reference for v3.0.0
- [docs/KNOWN_ISSUES_v3.0.0.md](docs/KNOWN_ISSUES_v3.0.0.md) - Known limitations and workarounds

**Getting Started:**
- [docs/getting_started.md](docs/getting_started.md) - Step-by-step developer guide
- [docs/QUICK_REFERENCE_DOCS.md](docs/QUICK_REFERENCE_DOCS.md) - Quick lookup guide for finding documentation

**Organization & Guidelines:**
- [docs/DOCUMENT_ORGANIZATION.md](docs/DOCUMENT_ORGANIZATION.md) - Complete documentation organization reference
- [docs/BEFORE_AFTER_ORGANIZATION.md](docs/BEFORE_AFTER_ORGANIZATION.md) - Visual before/after of documentation structure
- [docs/INDEX.md](docs/INDEX.md) - Master table of contents for all documentation

**Integration & Examples:**
- [docs/agent_integration.md](docs/agent_integration.md) - AI agent integration guide
- [docs/examples.md](docs/examples.md) - Code examples and use cases
- [examples/](examples/) - Runnable integration examples

**Deployment:**
- [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) - Quick Docker deployment
- [docs/deployment/](docs/deployment/) - Comprehensive deployment procedures and troubleshooting

**Security & Compliance:**
- [SECURITY.md](SECURITY.md) - Security policies and reporting
- [docs/compliance/](docs/compliance/) - Regulatory and audit documentation

## Contributing

```bash
git clone https://github.com/tescolopio/code-scalpel.git
cd code-scalpel
pip install -e ".[dev]"
pytest tests/
```

See [Contributing Guide](docs/guides/CONTRIBUTING.md) for details.

## Roadmap

See [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) for the complete roadmap.

> [20251218_DOCS] Release notes pointer updated for v3.0.0 "Autonomy"

- Latest release notes: [docs/release_notes/RELEASE_NOTES_v3.0.0.md](docs/release_notes/RELEASE_NOTES_v3.0.0.md)

| Version | Status | Release Date | Highlights |
|---------|--------|--------------|------------|
| **v1.5.x** | Released | Dec 13, 2025 | Cross-file analysis, context tools, project intelligence |
| **v2.0.0** | Released | Dec 15, 2025 | **Polyglot** - TypeScript, JavaScript, Java support |
| **v2.5.0** | Released | Dec 17, 2025 | **Guardian** - Policy engine, governance controls |
| **v3.0.0** | Current | Dec 18, 2025 | **Autonomy** - Self-correction, 4033 tests, 94.86% coverage |
| **v3.1.0** | Planned | Q1 2026 | Autonomy+ - Enhanced self-correction, enterprise demos |

**Strategic Focus:** MCP server toolkit enabling AI agents to perform surgical code operations without hallucination.

## Stats

- **4,033** tests passing (100% pass rate)
- **94.86%** combined coverage (statement + branch)
- **100%** coverage: PDG, AST, Symbolic Execution, Security Analysis, Cross-File Analysis
- **4** languages supported (Python, TypeScript, JavaScript, Java)
- **19** MCP tools for AI agents
- **17+** vulnerability types detected (SQL, XSS, NoSQL, LDAP, DOM XSS, Prototype Pollution, secrets)
- **30+** secret detection patterns (AWS, GitHub, Stripe, private keys)
- **200x** cache speedup
- **99%** token reduction via surgical extraction
- **Python 3.13** compatible

## License

MIT License - see [LICENSE](LICENSE)

"Code Scalpel" is a trademark of 3D Tech Solutions LLC.

---

**Built for the AI Agent Era** | [PyPI](https://pypi.org/project/code-scalpel/) | [GitHub](https://github.com/tescolopio/code-scalpel)

<!-- mcp-name: io.github.tescolopio/code-scalpel -->
