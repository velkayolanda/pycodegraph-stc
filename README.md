# pycodegraph

**Static Python code analysis with LLM-generated summaries and diagram rendering**

Statická analýza Pythonu přes AST, LLM anotace a generování Mermaid/PlantUML diagramů tříd a sekvencí.

## Purpose

`pycodegraph` is a CLI tool that statically analyzes Python projects (without execution) to:

1. Extract code structure into JSON (modules, classes, functions, imports, etc.)
2. Extract call sequences into JSON (with control flow tracking)
3. Generate LLM-powered summaries for code entities
4. Render class and sequence diagrams in Mermaid (or PlantUML)

The tool consists of three strictly independent stages that communicate only via JSON files:

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  Analyzer   │──────▶│  Annotator  │──────▶│  Renderer   │
│  .py files  │ JSON  │  LLM calls  │ JSON  │  Diagrams   │
│             │       │  + cache    │       │  (Mermaid)  │
└─────────────┘       └─────────────┘       └─────────────┘
    ↓                      ↓                      ↓
structure.json        annotations.json       *.mmd files
calls.json
```

## Installation

### Requirements

- Python 3.13 or higher
- pip or uv

### Install from source

```bash
git clone https://github.com/yourusername/pycodegraph-stc.git
cd pycodegraph-stc
pip install -e .
```

### Install with LLM provider support

```bash
# Install with specific provider
pip install -e ".[openai]"      # OpenAI (GPT-4, etc.)
pip install -e ".[anthropic]"   # Anthropic (Claude)
pip install -e ".[gemini]"      # Google Gemini
pip install -e ".[ollama]"      # Ollama (local models)

# Or install all providers
pip install -e ".[all]"
```

### Development installation

```bash
pip install -e ".[dev,all]"
```

## Quick Start

```bash
# 1. Analyze your Python project
pycodegraph analyze --src ./my_project --out ./output

# 2. Generate LLM summaries (requires API key)
export ANTHROPIC_API_KEY="your_api_key_here"
pycodegraph annotate --input ./output --provider anthropic --model claude-3-5-sonnet-20241022

# 3. Render diagrams
pycodegraph render --input ./output --diagram all

# 4. For sequence diagram, specify entry point
pycodegraph render --input ./output --diagram sequence --entry my_project.main.run --depth 3
```

## Configuration

Copy `.envň` to `.env` and configure your LLM provider:

```bash
cp .env .env
# Edit .env with your API keys and preferences
```

## CLI Reference

### `pycodegraph analyze`

Analyzes Python code and generates `structure.json` and `calls.json`.

```bash
pycodegraph analyze --src <source_dir> --out <output_dir> [--verbose]
```

**Options:**
- `--src`: Source directory containing Python files to analyze (required)
- `--out`: Output directory for JSON files (required)
- `--verbose`: Enable verbose logging

**Output:**
- `structure.json`: Complete code structure (modules, classes, functions, etc.)
- `calls.json`: Call sequences with control flow tracking

### `pycodegraph annotate`

Generates LLM summaries and creates `annotations.json`.

```bash
pycodegraph annotate --input <json_dir> [options]
```

**Options:**
- `--input`: Directory containing `structure.json` and `calls.json` (required)
- `--provider`: LLM provider (`openai`, `anthropic`, `gemini`, `ollama`)
- `--model`: Model name (e.g., `claude-3-5-sonnet-20241022`, `gpt-4`)
- `--lang`: Summary language code (default: `cs` for Czech)
- `--dry-run`: Show what would be processed without making API calls
- `--no-cache`: Disable cache (always query LLM)
- `--refresh`: Refresh all cached entries
- `--verbose`: Enable verbose logging

**Output:**
- `annotations.json`: LLM-generated summaries keyed by entity ID

**Privacy note:** The annotator sends your code to external LLM APIs. Use `--dry-run` to see what would be sent before committing.

### `pycodegraph render`

Renders Mermaid or PlantUML diagrams from JSON files.

```bash
pycodegraph render --input <json_dir> [options]
```

**Options:**
- `--input`: Directory containing JSON files (required)
- `--format`: Output format (`mermaid`, `plantuml`; default: `mermaid`)
- `--diagram`: Diagram type (`class`, `sequence`, `all`; default: `all`)
- `--entry`: Entry point for sequence diagram (fully qualified name, e.g., `app.main.run`)
- `--depth`: Maximum depth for sequence diagram (default: 3)
- `--output`: Output file path (default: stdout)
- `--verbose`: Enable verbose logging

**Output:**
- `.mmd` files (Mermaid) or `.puml` files (PlantUML)

## JSON Format

### structure.json

Contains the complete code structure with fully qualified IDs for every entity.

**Entity types:**
- Modules
- Imports (with aliases)
- Global variables/constants
- Classes (with bases, attributes, methods)
- Functions/methods (with arguments, return types, decorators)

**Key features:**
- Every entity has a fully qualified `id` (e.g., `app.models.OrderProcessor.process`)
- Type hints preserved
- Line numbers for all entities
- Inheritance relationships

### calls.json

Contains call sequences per function/method in evaluation order.

**Key features:**
- Calls ordered by evaluation (e.g., in `f(g(x))`, `g` appears before `f`)
- Control-flow stack tracking (`if/elif/else`, `for`, `while`, `try/except/finally`, `with`)
- Each control-flow block has a unique `block_id` for grouping in diagrams
- Target resolution with categories: `local_function`, `self_method`, `inherited_method`, `class_instantiation`, `imported_call`, `builtin`, `attribute_call`, `unresolved`

### annotations.json

Contains LLM-generated summaries keyed by entity ID.

**Key features:**
- One-to-two sentence summaries focusing on purpose
- Metadata: model name, prompt version, cache key hash
- Bottom-up generation (leaf functions first, so callee summaries can be context)

## LLM Provider Setup

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
pycodegraph annotate --input ./output --provider openai --model gpt-4
```

### Anthropic (Claude)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
pycodegraph annotate --input ./output --provider anthropic --model claude-3-5-sonnet-20241022
```

### Google Gemini

```bash
export GEMINI_API_KEY="..."
pycodegraph annotate --input ./output --provider gemini --model gemini-1.5-pro
```

### Ollama (Local)

```bash
# Start Ollama server first: ollama serve
export OLLAMA_HOST="http://localhost:11434"
pycodegraph annotate --input ./output --provider ollama --model llama2
```

## Supported Python Constructs

| Construct | Supported | Notes |
|-----------|-----------|-------|
| Modules | ✅ | Full support with dotted names |
| Imports | ✅ | Including aliases and relative imports |
| Classes | ✅ | With inheritance and attributes |
| Functions/Methods | ✅ | With decorators, type hints, defaults |
| Instance attributes | ✅ | From `self.x = ...` assignments |
| Class attributes | ✅ | Including annotated attributes |
| Call sequences | ✅ | In evaluation order |
| Control flow | ✅ | if/elif/else, for, while, try/except/finally, with |
| Nested calls | ✅ | e.g., `f(g(x))` |
| Chained calls | ✅ | e.g., `a.b().c()` |
| Async functions | 🚧 | Partial support (bonus feature) |
| Comprehensions | ⚠️ | Flattened or skipped (documented) |
| Lambdas | ⚠️ | Flattened or skipped (documented) |
| Dynamic code | ❌ | `exec`, `eval`, dynamic imports not supported |

## Privacy and Security

**Important:** The `annotate` command sends your source code to external LLM APIs. Consider:

- Use `--dry-run` first to see what would be sent
- Review which entities will be annotated
- Use Ollama with local models for sensitive code
- The cache stores source hashes, not raw code

## Limitations

- **Static analysis only**: No code execution, so runtime behavior is not captured
- **Type inference**: Basic inference from annotations and assignments; complex dynamic types may be `unresolved`
- **Third-party libraries**: Only imports are tracked; internal structure of libraries is not analyzed
- **Dynamic constructs**: `exec`, `eval`, and dynamic imports are not supported
- **Nested/lambda calls**: May be flattened or skipped (see docs)

## Development

### Running tests

```bash
pytest
```

### Code quality

```bash
ruff check .
ruff format .
```

### Project structure

```
src/pycodegraph/
  cli.py                    # Command-line interface
  model.py                  # Pydantic models (source of truth)
  analyzer/                 # Stage 1: Extract structure and calls
    discovery.py
    structure.py
    calls.py
    resolver.py
  annotator/                # Stage 2: Generate LLM summaries
    context.py
    cache.py
    annotate.py
    providers/              # LLM provider implementations
  renderer/                 # Stage 3: Generate diagrams
    loader.py
    class_diagram.py
    sequence_diagram.py
    mermaid.py
schema/                     # Generated JSON schemas
tests/                      # Test suite
  sample_project/           # Reference test project
  expected/                 # Golden JSON outputs
```

## Design Decisions

1. **Fully qualified IDs**: Every entity has a unique ID like `app.models.User.save`
2. **Three independent stages**: Analyzer → Annotator → Renderer communicate only via JSON
3. **Annotations separate from structure**: Summaries in `annotations.json`, not `structure.json`
4. **Control-flow as a stack**: Nested blocks tracked as a list, outermost first
5. **Evaluation-order calls**: Custom AST visitor ensures `f(g(x))` has `g` before `f`
6. **Lightweight type inference**: Basic inference without heavy dependencies
7. **SHA-256 cache**: Cache key includes code, prompt version, and model name
8. **Bottom-up annotation**: Leaf functions first, so callees are already summarized

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please:

1. Follow PEP 8 (enforced by ruff)
2. Add type hints
3. Write tests for new features
4. Use Conventional Commits
5. Keep commits small and focused

## Acknowledgments

This project was developed as part of a software engineering course assignment.
