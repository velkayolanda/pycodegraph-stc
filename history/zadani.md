# pycodegraph-stc — implementation task list

Hand-off brief for the coding assistant. The original assignment is in `docs/zadani.pdf` (Czech). This file lists
everything to build and the design decisions already made (they refine or fix the assignment, so follow them).

## Project summary

CLI tool that statically analyzes a Python project (no execution), writes `structure.json` and `calls.json`,
adds LLM-generated summaries, and renders Mermaid class and sequence diagrams.

Three strictly independent stages communicating only via JSON files:

1. **Analyzer** (`.py` → `structure.json`, `calls.json`)
2. **Annotator** (JSON → `annotations.json`, LLM + hash cache)
3. **Renderer** (JSON only, never reads `.py` → Mermaid)

## Conventions

- Package name `pycodegraph`, repo `pycodegraph-stc`, `src/` layout, CLI command `pycodegraph`.
- Python 3.13 (`requires-python = ">=3.13"`). Type hints everywhere. PEP 8, checked with ruff.
- Code, identifiers, comments, commit messages in English. User-facing docs may be Czech/English.
- LLM-generated summaries default to Czech (configurable, `--lang`).
- Data model with Pydantic (or dataclasses). Keep AST walking separate from the data model.
- Conventional Commits, small commits, one stage at a time. Never commit `.env` or the LLM cache.

## Target layout

```
src/pycodegraph/
  cli.py
  model.py                 # shared pydantic models = source of truth for JSON schemas
  analyzer/
    discovery.py           # walk dirs, ignore .git/.venv/__pycache__, build module names
    structure.py           # structure.json extractor
    calls.py               # calls.json extractor
    resolver.py            # target resolution
  annotator/
    context.py             # per-entity context (code slice, docstring, signature, callees)
    cache.py               # SHA-256 keyed local cache
    providers/             # base.py, openai.py, anthropic.py, gemini.py, ollama.py
    annotate.py
  renderer/
    loader.py              # loads + merges the JSON files
    class_diagram.py
    sequence_diagram.py
    mermaid.py             # escaping helpers
schema/                    # generated JSON Schemas
tests/
  sample_project/          # reference project
  expected/                # golden JSON outputs
```

## Design decisions (deviations from / clarifications of the assignment)

1. **Every entity has a fully qualified `id`**, e.g. `app.models.OrderProcessor.process`. Applies to modules,
   classes, methods, functions, globals. `bases` are stored as qualified ids when resolvable, otherwise as raw text
   plus `"resolved": false`.
2. **Summaries live in `annotations.json`**, not in `structure.json`, keyed by entity `id`. The extractor never
   writes `summary`. The renderer merges `annotations.json` if present and works without it.
3. **`control_flow` is a list (stack) of enclosing blocks**, outermost first, not a single object. Each block:
   `{"type": "if|elif|else|for|while|try|except|finally|with", "block_id": "<unique per block>", "branch": "...", "condition": "<source text or null>"}`.
   `block_id` lets the renderer group calls into one `alt`/`opt`/`loop`.
4. **Call order = evaluation order.** Use a custom `ast.NodeVisitor`, not `ast.walk`. In `f(g(x))`, `g` comes
   before `f`. Chained calls `a.b().c()` are emitted left to right.
5. **Extended target categories** (superset of the assignment): `local_function`, `self_method`, `inherited_method`,
   `class_instantiation`, `imported_call`, `builtin`, `attribute_call`, `unresolved`.
6. **Lightweight type inference without `jedi`** to avoid most `unresolved` results: infer attribute types from
   `self.x = Foo()` and from annotations on `__init__` parameters / class-level annotations; resolve
   `self.x.method()` through that. `jedi` is an optional bonus only.
7. **Mermaid is the required output.** PlantUML is optional, behind the same renderer interface.
8. **Cache key** = SHA-256 of (entity source + prompt version + model name + serialized callee list). Changing the
   prompt, model, or code invalidates it.
9. **Sequence diagram `--depth N`** (default 3) with cycle/recursion detection (stop and mark `...recursive`).
10. **Formal JSON Schemas** are generated from the models and used in tests for validation.

## Tasks

Mark each when done. Do them in this order. Each task must leave tests green.

### 0. Project setup
- [ ] `pyproject.toml` (build backend, `requires-python`, deps: pydantic, click, pytest, ruff; optional extras per LLM provider).
- [ ] `.gitignore` additions: `.env`, `.pycodegraph_cache/`, `output/`, `.venv/`.
- [ ] `../.env` with `PYCODEGRAPH_PROVIDER`, `PYCODEGRAPH_MODEL`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `OLLAMA_HOST`.
- [ ] Package skeleton with empty modules and CLI stub (`analyze`, `annotate`, `render`).
- [ ] ruff config, pytest config, README skeleton.

### 1. Data model and schemas
- [ ] Pydantic models: `Project`, `Module`, `Import`, `GlobalVar`, `ClassDef`, `Attribute`, `FunctionDef`, `Arg`.
- [ ] Models for calls: `CallSequence`, `Call`, `ControlFlowBlock`, `TargetCategory` enum.
- [ ] Model for `Annotations` (id → summary, plus meta: model, prompt_version, hash).
- [ ] Script/command that exports JSON Schemas to `schema/`.
- [ ] Unit tests: model round-trip, schema export matches committed files.

### 2. Analyzer — structure.json
- [ ] Discovery: recursive walk, ignore hidden/system dirs, map files to dotted module names, handle packages with `__init__.py`.
- [ ] Imports with aliases (`import x as y`, `from x import y as z`, relative imports resolved to absolute).
- [ ] Module-level globals/constants with type hints and line numbers.
- [ ] Classes: bases, class attributes, instance attributes from `self.x = ...` in any method (mainly `__init__`), annotated attributes, methods, line numbers.
- [ ] Functions/methods: args (with type hints, defaults), return type, decorators, line numbers (and end line for source slicing).
- [ ] Qualified `id` on every entity.
- [ ] Robust error handling: syntax errors in a file are reported and skipped, not fatal.
- [ ] Bonus-ready: handle `AsyncFunctionDef` the same way (flag `is_async`).

### 3. Analyzer — calls.json
- [ ] Per function/method call sequence in evaluation order with `step`, `target`, `line`.
- [ ] Control-flow stack for `if/elif/else`, `for`, `while` (also `try/except/finally`, `with`). Provide `block_id` and `branch`.
- [ ] Handle nested calls, chained calls, calls in comprehensions/lambdas (decide and document: either flattened or skipped), nested functions.
- [ ] Target resolution with the extended categories; use import alias map, class method table, base-class lookup, and attribute type inference (decision 6).
- [ ] `resolved_target` as fully qualified id when known, else `null` with category `unresolved`.
- [ ] Optional: `await` handling for async code.

### 4. Annotator
- [ ] Context builder: source slice via AST line coordinates (needs the project path, read-only), docstring, signature, callee list from `calls.json`.
- [ ] Provider interface + at least one real provider (e.g. Anthropic or OpenAI) and Ollama for local use. Config via env vars and CLI flags.
- [ ] Structured output enforced (JSON mode / structured outputs / tool call). Output: `{"summary": "<1–2 sentences, purpose not line-by-line paraphrase>"}`.
- [ ] Processing order bottom-up (leaf functions first, then callers, then classes) so callee summaries can be context.
- [ ] SHA-256 cache on disk (decision 8). Only changed entities are re-queried. `--no-cache` and `--refresh` flags.
- [ ] Retry with backoff, timeout, handling of invalid JSON, rate limits; failed entities are reported and skipped, run continues.
- [ ] Write `annotations.json`. Temperature 0. Summary language via `--lang` (default `cs`).
- [ ] Prompt kept in one file with a `PROMPT_VERSION` constant.
- [ ] Dry-run mode listing which entities would be sent (privacy: code is sent to an external API).

### 5. Renderer
- [ ] Loader: read `structure.json`, `calls.json`, optional `annotations.json`. Must not touch `.py` files.
- [ ] Class diagram (Mermaid `classDiagram`): classes, attributes, methods with parameters and return types, inheritance, basic associations (from attribute types and constructor calls), class summaries as notes.
- [ ] Sequence diagram (Mermaid `sequenceDiagram`) for `--entry <qualified id>`: participants (module or class, configurable), nested `alt/else/opt/loop` from the control-flow stack, optional step summaries, `--depth`, recursion guard.
- [ ] Mermaid escaping: generics (`list[dict]` → `list~dict~`), special chars in notes/labels, Czech diacritics.
- [ ] Output to files (`.mmd`) and optionally to stdout.
- [ ] Optional: PlantUML backend behind the same interface.

### 6. CLI
- [ ] `pycodegraph analyze --src DIR --out DIR`
- [ ] `pycodegraph annotate --input DIR --provider NAME [--model M] [--lang cs] [--dry-run] [--no-cache]`
- [ ] `pycodegraph render --input DIR --format mermaid --entry app.main.run [--depth N] [--diagram class|sequence|all]`
- [ ] Clear error messages, non-zero exit codes, `--verbose` logging.

### 7. Tests (pytest)
- [ ] `tests/sample_project/`: small realistic project covering packages, aliases, inheritance, `self.*` attributes, if/elif/else, for/while, nested control flow, class instantiation, imported calls, unresolved calls, an async function.
- [ ] Golden tests: analyzer output vs `tests/expected/*.json`.
- [ ] Schema validation of every generated JSON file.
- [ ] Annotator with a mocked provider: structured output parsing, cache hit/miss, only changed entities re-queried, invalidation on prompt/model change, failure handling.
- [ ] Renderer: snapshot tests for class and sequence diagrams, nested blocks, depth limit, recursion guard, rendering without annotations.
- [ ] CLI tests (click `CliRunner`) for all three commands.

### 8. Docs and quality
- [ ] README: purpose, install, quick start, full CLI examples, JSON format description, supported/unsupported constructs table, LLM provider setup, privacy note, limitations.
- [ ] Architecture section (stage diagram) and a short "design decisions" section.
- [ ] Example output committed under `examples/` (JSON + rendered `.mmd`).
- [ ] ruff clean, tests green, type hints complete.

### 9. Bonus (only after everything above works)
- [ ] `jedi` integration for precise inference on dynamic calls.
- [ ] Full `async/await` support in calls and diagrams.
- [ ] PlantUML renderer.

## Definition of done

- All three CLI commands work end to end on `tests/sample_project`.
- The renderer works with only the JSON files (verified by a test that deletes the sources).
- Re-running `annotate` without code changes makes zero LLM calls.
- All generated JSON validates against the schemas in `schema/`.
- `pytest` and `ruff` pass; README is complete.