# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Cookiecutter template for entity resolution projects. It generates Python projects with a modular architecture designed for data extraction, processing, and storage workflows.

## Architecture

The generated projects follow a 4-layer architecture:

1. **Extractors** (`src/extractors/`) - Data gathering and parsing from various sources (web scraping, APIs, files, databases)
2. **Storage** (`src/storage/`) - Data persistence layer with pluggable backends (SQLite, PostgreSQL, Neo4j, MongoDB)
3. **Pipeline** (`src/pipeline/`) - Async/parallel data processing workflows (Prefect, Dagster, or simple pipeline)
4. **API** (`src/api/`) - REST or search API endpoints (FastAPI, Flask, Django, or none)
5. **Ontology** (`src/ontology/`) - LLM-powered database schema inspection and knowledge graph ontology generation

Core configuration is managed through `src/config/settings.py` using Pydantic settings with environment variable support.

## Template Configuration

The template uses `cookiecutter.json` to configure:
- **Data sources**: web_scraping, api_scraping, files, database
- **Storage backends**: sqlite, postgresql, neo4j, mongodb
- **Pipeline orchestrators**: prefect, dagster
- **API frameworks**: fastapi, flask, django, none
- **Search engines**: none, vector_hybrid, elasticsearch
- **Optional features**:
  - `include_ontology_generator` - Adds ontology generation capabilities
  - `include_web_scraping`, `include_api_scraping`, `include_vector_search`, `include_nlp`
  - `use_docker`, `use_pytest`

## Development Commands

**Template Generation:**
```bash
cookiecutter .                            # Generate with interactive prompts
cookiecutter . --no-input                 # Generate with default values
cookiecutter . --no-input database=postgresql api_framework=flask
cookiecutter . --replay                   # Replay last generation
cookiecutter . --overwrite-if-exists      # Force re-generation
```

**Testing Template in Temporary Directory:**
```bash
cd /tmp && cookiecutter /path/to/entity-resolution-cookiecutter --no-input
```

Generated projects include these standardized commands via `pyproject.toml`:

**Installation:**
```bash
pip install -e .         # Development install
pip install -e ".[dev]"  # With dev dependencies
```

**Testing:**
```bash
pytest                   # Run all tests
pytest --cov             # Run with coverage
pytest -m "not slow"     # Skip slow tests
```

**Code Quality:**
```bash
black src/ tests/        # Format code
isort src/ tests/        # Sort imports
mypy src/                # Type checking
```

**Ontology Generation (if enabled):**
```bash
python src/ontology/schema_inspector.py 'postgresql://user:pass@localhost/db'
python src/ontology/llm_designer.py 'postgresql://user:pass@localhost/db' MyOntology
# Requires ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable
```

## Template Development

When working on the cookiecutter template itself:
- Template files are in `{{cookiecutter.project_slug}}/`
- Variables use Jinja2 syntax: `{{ cookiecutter.variable_name }}`
- Conditional content uses `{% if cookiecutter.option %}` blocks
- Post-generation cleanup handled by `hooks/post_gen_project.py`

**Template Structure:**
- `cookiecutter.json` - Template configuration and variables
- `hooks/pre_gen_project.py` - Pre-generation validation (currently empty)
- `hooks/post_gen_project.py` - Post-generation cleanup that:
  - Removes unused pipeline files (prefect/dagster/simple)
  - Removes unused database storage files
  - Renames selected API framework directory to `src/api/` and removes others
  - Removes optional features based on selections (web scraping, API scraping, vector search, NLP)
- `{{cookiecutter.project_slug}}/` - Main template directory with all possible options

**Important Post-Hook Behavior:**
The hook runs inside the generated project directory and uses `Path(".")` to reference the project root. It conditionally:
1. Keeps only the selected orchestrator's pipeline file
2. Keeps only the selected database's storage file
3. Renames the selected API framework directory (e.g., `api_fastapi/` → `api/`)
4. Removes feature directories when not selected (e.g., `src/matchers/`, `src/embeddings/`)

## Key Components

**Ontology Generation Module** (`src/ontology/`):
- `schema_inspector.py` - PostgreSQL schema introspection with comprehensive metadata extraction (columns, foreign keys, indexes, row counts)
- `llm_designer.py` - LLM-powered ontology design supporting Anthropic (Claude) and OpenAI (GPT)
  - Analyzes database schemas to generate knowledge graph ontologies
  - Identifies entity classes, properties, and relationships
  - Supports entity resolution focus with natural key identification
  - Provides ontology refinement, design explanations, and improvement suggestions
  - Outputs JSON ontology definitions

**Multi-Framework API Support:**
Template maintains separate directories (`api_fastapi/`, `api_flask/`, `api_django/`) that get renamed/removed by the post-hook based on selection. This allows different frameworks with different file structures.

**Conditional Dependencies:**
The `pyproject.toml` uses Jinja2 conditionals to include only dependencies for selected features, keeping generated projects lightweight.