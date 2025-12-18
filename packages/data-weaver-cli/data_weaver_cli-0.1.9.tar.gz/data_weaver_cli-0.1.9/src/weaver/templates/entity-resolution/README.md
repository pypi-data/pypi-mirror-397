# ER cookiecutter

This is a base template for entity resolution projects. The core components are:
- extractors - for gathering and parsing from data sources
- storage - data store interface
- pipeline - async and/or parallel, long-running data processing
- api - REST or search API

## Usage

Generate a new project from this template:

```bash
cookiecutter .
```

Or with default values:

```bash
cookiecutter . --no-input
```

## How to Test Hooks

The `hooks/post_gen_project.py` script runs after project generation to clean up unused files based on your selections. Here's how to test it:

### Basic Testing

```bash
# Test with default values (no prompts)
cookiecutter . --no-input

# Test with specific values
cookiecutter . --no-input database=postgresql api_framework=flask

# Test in a temp directory to avoid clutter
cd /tmp && cookiecutter /path/to/entity-resolution-cookiecutter --no-input

# Test with replay (reuse last answers)
cookiecutter . --replay

# Force re-generation (overwrite existing)
cookiecutter . --overwrite-if-exists
```

### Debugging Hooks

Add debug output to `hooks/post_gen_project.py`:

```python
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current dir: {os.listdir('.')}")
print(f"Selected options: orchestrator={orchestrator}, api_framework={api_framework}")
```

### Verifying Hook Behavior

After generation, verify the hook cleaned up correctly:

```bash
# Check only selected API framework exists
ls src/api_*  # Should fail (directories removed)
ls src/api    # Should exist with your chosen framework

# Check optional features removed when not selected
ls src/matchers   # Should only exist if include_nlp=yes
ls src/embeddings # Should only exist if include_vector_search=yes
```

### Common Issues

- **Hook doesn't run**: Ensure `hooks/post_gen_project.py` is executable and has no syntax errors
- **Files not cleaned up**: The hook runs inside the generated project directory, so use `Path(".")` not `Path(project_slug)`
- **Permission errors**: Ensure the hook has permission to delete files/directories