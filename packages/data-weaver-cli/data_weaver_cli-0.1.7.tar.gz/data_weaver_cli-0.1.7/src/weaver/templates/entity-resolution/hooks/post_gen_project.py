# hooks/post_gen_project.py
import os
import shutil
from pathlib import Path


def remove_file_or_dir(path):
    """Remove a file or directory"""
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)


def main():
    # Get cookiecutter variables
    orchestrator = "{{ cookiecutter.orchestrator }}"
    api_framework = "{{ cookiecutter.api_framework }}"
    database = "{{ cookiecutter.database }}"
    include_web_scraping = "{{ cookiecutter.include_web_scraping }}"
    include_api_scraping = "{{ cookiecutter.include_api_scraping }}"
    include_vector_search = "{{ cookiecutter.include_vector_search }}"
    include_nlp = "{{ cookiecutter.include_nlp }}"
    include_ontology_generator = "{{ cookiecutter.include_ontology_generator }}"

    project_slug = "{{ cookiecutter.project_slug }}"
    base_path = Path(".")

    # Remove unused pipeline files
    pipeline_path = base_path / "src" / "pipeline"
    if orchestrator != "prefect":
        remove_file_or_dir(pipeline_path / "prefect_flows.py")
    if orchestrator != "dagster":
        remove_file_or_dir(pipeline_path / "dagster_flows.py")
    if orchestrator != "simple":
        remove_file_or_dir(pipeline_path / "simple_pipeline.py")

    # Remove unused database storage files
    storage_path = base_path / "src" / "storage"
    if database != "sqlite":
        remove_file_or_dir(storage_path / "storage_sqlite.py")
    if database != "postgresql":
        remove_file_or_dir(storage_path / "storage_pg.py")
    if database != "neo4j":
        remove_file_or_dir(storage_path / "storage_neo4j.py")

    # Handle API framework - keep one, remove others
    src_path = base_path / "src"
    if api_framework == "fastapi":
        # Rename api_fastapi to api
        if (src_path / "api_fastapi").exists():
            if (src_path / "api").exists():
                shutil.rmtree(src_path / "api")
            (src_path / "api_fastapi").rename(src_path / "api")
        remove_file_or_dir(src_path / "api_flask")
        remove_file_or_dir(src_path / "api_django")

    elif api_framework == "flask":
        if (src_path / "api_flask").exists():
            if (src_path / "api").exists():
                shutil.rmtree(src_path / "api")
            (src_path / "api_flask").rename(src_path / "api")
        remove_file_or_dir(src_path / "api_fastapi")
        remove_file_or_dir(src_path / "api_django")

    elif api_framework == "django":
        if (src_path / "api_django").exists():
            if (src_path / "api").exists():
                shutil.rmtree(src_path / "api")
            (src_path / "api_django").rename(src_path / "api")
        remove_file_or_dir(src_path / "api_fastapi")
        remove_file_or_dir(src_path / "api_flask")

    elif api_framework == "none":
        remove_file_or_dir(src_path / "api_fastapi")
        remove_file_or_dir(src_path / "api_flask")
        remove_file_or_dir(src_path / "api_django")
        remove_file_or_dir(src_path / "api")

    # Remove unused web scraping and API scraping files
    extractors_path = base_path / "src" / "extractors"
    if include_web_scraping != "yes":
        remove_file_or_dir(extractors_path / "requests_beautifulsoup.py")
        remove_file_or_dir(extractors_path / "playwright.py")

    if include_api_scraping != "yes":
        remove_file_or_dir(extractors_path / "api_extractor.py")

    # Remove optional features if not selected
    if include_vector_search != "yes":
        remove_file_or_dir(src_path / "search" / "vector_store.py")
        remove_file_or_dir(src_path / "embeddings")

    if include_nlp != "yes":
        remove_file_or_dir(src_path / "matchers")

    if include_ontology_generator != "yes":
        remove_file_or_dir(src_path / "ontology")

    print("✅ Project structure cleaned up based on selections!")


if __name__ == "__main__":
    main()