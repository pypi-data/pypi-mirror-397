# Code Scalpel

[![PyPI version](https://badge.fury.io/py/code-scalpel.svg)](https://pypi.org/project/code-scalpel/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-2580%20passed-brightgreen.svg)](https://github.com/tescolopio/code-scalpel)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](release_artifacts/v2.0.0/)

**MCP Server Toolkit for AI Agents**

Code Scalpel enables AI assistants (Claude, GitHub Copilot, Cursor) to perform surgical code operations without hallucination. Extract exactly what's needed, modify without collateral damage, verify before applying.

```bash
pip install code-scalpel==2.0.0
```

> **v2.0.0 "POLYGLOT" RELEASE** (December 15, 2025)  
> Multi-Language Support + Advanced MCP Protocol Features
>
> | Component | Status | Notes |
> |-----------|--------|-------|
> | Languages | **4** | Python, TypeScript, JavaScript, Java |
> | Security Scanning | **17+ types** | SQL, XSS, NoSQL, LDAP, DOM XSS, Prototype Pollution |
> | Cross-File Analysis | **STABLE** | Import resolution, taint tracking, extraction |
> | MCP Protocol | **COMPLETE** | Health endpoint, Progress tokens, Roots capability |
> | Token Efficiency | **99%** | Surgical extraction vs full file |
> | Performance | **20,000+ LOC/sec** | Project-wide analysis |
> | MCP Tools | **15 tools** | analyze, extract, security, test-gen, cross-file |
>
> **What's New in v2.0.0:**
> - **Multi-Language**: TypeScript, JavaScript, Java extraction and security scanning
> - **Health Endpoint**: `/health` for Docker container monitoring (port 8594)
> - **Progress Tokens**: Real-time progress for `crawl_project`, `cross_file_security_scan`
> - **Roots Capability**: Workspace discovery via `ctx.list_roots()`
> - **Windows Path Support**: Full backslash handling across all tools
> - **Best-in-Class Validated**: F1=1.0 security detection, 99% token reduction
>
> See [RELEASE_NOTES_v2.0.0.md](docs/release_notes/RELEASE_NOTES_v2.0.0.md) for technical details.

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
| Pattern matching (regex) | ✓ | **Taint tracking** through variables |
| Single file analysis | ✓ | **Cross-file** dependency graphs |
| Manual test writing | ✓ | **Z3-powered** test generation |
| Generic output | ✓ | **AI-optimized** structured responses |
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

## AI Agent Integration

### GitHub Copilot (VS Code)

Create `.vscode/mcp.json`:

```json
{
  "servers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp", "--root", "${workspaceFolder}"]
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp", "--root", "/path/to/project"]
    }
  }
}
```

### MCP Tools Available (15 Total)

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

**Cross-File Tools (v1.5.1) - NEW**
| Tool | Description |
|------|-------------|
| `get_cross_file_dependencies` | Build import graphs and resolve symbols |
| `cross_file_security_scan` | Detect vulnerabilities spanning modules |

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

- [Getting Started](docs/getting_started.md)
- [API Reference](docs/api_reference.md)
- [Agent Integration Guide](docs/agent_integration.md)
- [Demo Suite](demos/README.md)

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

| Version | Status | Release Date | Highlights |
|---------|--------|--------------|------------|
| **v1.3.0** | ✅ Released | Dec 7, 2025 | NoSQL/LDAP injection, hardcoded secrets |
| **v1.4.0** | ✅ Released | Dec 10, 2025 | Context tools (file_context, symbol_references, call_graph) |
| **v1.5.0** | ✅ Released | Dec 12, 2025 | Project intelligence (project_map, call_graph, scan_dependencies) |
| **v1.5.1** | ✅ Current | Dec 13, 2025 | **Cross-file analysis** (ImportResolver, CrossFileExtractor, CrossFileTaintTracker) |
| **v1.5.2** | Planned | Dec 16, 2025 | TestFix - Fix OSV client test isolation |
| **v1.5.3** | Planned | Dec 21, 2025 | PathSmart - Docker path resolution middleware |
| **v1.5.4** | Planned | Dec 29, 2025 | DynamicImports - Track importlib.import_module() |
| **v1.5.5** | Planned | Jan 8, 2026 | ScaleUp - Performance optimization for 1000+ file projects |
| **v2.0.0** | Planned | Q1 2026 | Polyglot (TypeScript/JavaScript full support) |

**Strategic Focus:** MCP server toolkit enabling AI agents to perform surgical code operations without hallucination.

## Stats

- **2,238** tests passing (149 new in v1.5.1)
- **100%** coverage: PDG, AST, Symbolic Execution, Security Analysis, Cross-File Analysis
- **95%+** coverage: Surgical Tools (SurgicalExtractor 95%, SurgicalPatcher 96%)
- **3** languages supported (Python full, JS/Java structural)
- **15** MCP tools for AI agents
- **16** vulnerability types detected (SQL, XSS, NoSQL, LDAP, command injection, path traversal, secrets, XXE)
- **30+** secret detection patterns (AWS, GitHub, Stripe, private keys)
- **200x** cache speedup
- **100%** external testing validation (16/16 vulnerabilities detected)

## License

MIT License - see [LICENSE](LICENSE)

"Code Scalpel" is a trademark of 3D Tech Solutions LLC.

---

**Built for the AI Agent Era** | [PyPI](https://pypi.org/project/code-scalpel/) | [GitHub](https://github.com/tescolopio/code-scalpel)

<!-- mcp-name: io.github.tescolopio/code-scalpel -->
