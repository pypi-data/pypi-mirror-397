# Weaver

Python project scaffolding tool that generates entity-resolution projects from bundled cookiecutter templates.

## Features

- Generate complete entity-resolution projects with a single command
- Multiple project templates optimized for different use cases
- LLM-powered ontology generation for knowledge graphs
- Integrated support for databases, orchestrators, APIs, and search engines
- Docker and testing support out of the box

## Installation

```bash
pip install weaver
```

Or install from source:

```bash
git clone https://github.com/yourusername/weaver.git
cd weaver
uv sync
```

## Quick Start

Create a new project:

```bash
# Create a knowledge graph project
weaver create --template knowledge-graph --name my-project

# Create an advanced search project
weaver create --template advanced-search --name my-search-app

# List available templates
weaver list-templates
```

## CLI Commands

### `create`
Generate a new project from a template.

```bash
weaver create --template <template-name> --name <project-name> [options]
```

**Options:**
- `--name`, `-n` - Name of your project
- `--template`, `-t` - Project template to use (see available templates below)
- `--list-deps` - Show dependencies without creating project

**Knowledge Graph Options:**
- `--ontology` / `--no-ontology` - Enable/disable ontology generation (default: enabled)
- `--llm anthropic|openai` - LLM provider for ontology generation (default: anthropic)
- `--db-host` - Database host for schema inspection (default: localhost)
- `--db-port` - Database port for schema inspection (default: 5432)

**Examples:**

```bash
# Basic knowledge graph project
weaver create --template knowledge-graph --name company-kg

# Knowledge graph with OpenAI for ontology generation
weaver create --template knowledge-graph --name my-kg --llm openai

# Advanced search project
weaver create --template advanced-search --name search-engine

# Show dependencies without creating project
weaver create --template knowledge-graph --name test --list-deps
```

### `list-templates`
List all available project templates.

```bash
weaver list-templates
```

### `templates`
Show detailed information about available templates.

```bash
weaver templates
```

### `version`
Show Weaver version.

```bash
weaver version
```

## Available Templates

### `knowledge-graph`
Build knowledge graphs with Neo4j, web scraping, and LLM-powered ontology generation.

**Includes:**
- Neo4j graph database
- Web scraping and API data extraction
- Prefect orchestration
- FastAPI endpoints
- NLP processing
- LLM-powered ontology designer
- Schema inspection tools

**Best for:** Entity resolution, knowledge graphs, relationship mapping

**See the full demo:** [Knowledge Graph Demo Guide](DEMO_KNOWLEDGE_GRAPH.md)

### `advanced-search`
Hybrid sparse and vector search system optimized for complex queries.

**Includes:**
- PostgreSQL with vector extensions
- Hybrid vector + keyword search
- Prefect orchestration
- FastAPI search endpoints
- Web scraping

**Best for:** Search engines, recommendation systems, semantic search

### `news-analyzer`
News aggregation and analysis with bias detection.

**Includes:**
- PostgreSQL database
- NLP processing
- Vector search
- Elasticsearch
- API and web scraping

**Best for:** Content analysis, news aggregation, sentiment analysis

### `basic`
Simple entity-relationship project for quick prototyping.

**Includes:**
- SQLite database
- Simple orchestrator
- Basic project structure

**Best for:** Learning, prototyping, simple data projects

## Project Structure

Generated projects follow a consistent architecture:

```
my-project/
├── src/
│   ├── extractors/         # Data gathering (web, API, files, DB)
│   ├── storage/            # Database integration
│   ├── pipeline/           # Orchestration workflows
│   ├── api/                # REST/search endpoints (optional)
│   ├── ontology/           # Schema inspection & ontology generation (optional)
│   └── config/
│       └── settings.py     # Configuration with env variables
├── tests/
├── pyproject.toml
├── README.md
├── .env.example
└── docker-compose.yml      # If Docker enabled
```

## Knowledge Graph with Ontology Generation

Weaver's knowledge graph template includes powerful LLM-based ontology generation:

```bash
# Create knowledge graph project
weaver create --template knowledge-graph --name company-kg --ontology

cd company-kg

# Set your API key
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Inspect database schema
python -m src.ontology.schema_inspector 'postgresql://user:pass@localhost/mydb'

# Generate ontology from schema using Claude
python -m src.ontology.llm_designer 'postgresql://user:pass@localhost/mydb' MyOntology
```

The ontology generator will:
- Analyze your database schema
- Identify entity classes and relationships
- Detect natural keys for entity resolution
- Generate properties and cardinality constraints
- Provide design explanations and improvement suggestions
- Export as JSON for implementation in Neo4j

**Complete walkthrough:** See [DEMO_KNOWLEDGE_GRAPH.md](DEMO_KNOWLEDGE_GRAPH.md) for a full step-by-step demo with sample data.

## Configuration

Each template supports different configurations:

- **Databases:** SQLite, PostgreSQL, Neo4j, MongoDB
- **Orchestrators:** Prefect, Dagster, Simple
- **Search Engines:** Vector Hybrid, Elasticsearch, None
- **API Frameworks:** FastAPI, Flask, Django, None
- **Features:** Vector search, NLP, web scraping, API scraping, Docker, pytest

## Development

```bash
# Install dependencies
uv sync

# Run tests
pytest

# Run CLI locally
uv run weaver --help

# Build package
uv build
```

## Requirements

- Python 3.8+
- PostgreSQL (for ontology generation and some templates)
- Neo4j (for knowledge graph template)
- LLM API key (Anthropic or OpenAI) for ontology generation

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Resources

- [Knowledge Graph Demo](DEMO_KNOWLEDGE_GRAPH.md) - Complete walkthrough with ontology generation
- [Cookiecutter Documentation](https://cookiecutter.readthedocs.io/)
- [Neo4j Graph Database](https://neo4j.com/docs/)
- [Prefect Workflows](https://docs.prefect.io/)
- [Anthropic API](https://docs.anthropic.com/)
