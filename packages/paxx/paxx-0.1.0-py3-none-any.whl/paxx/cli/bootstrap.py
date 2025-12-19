"""CLI command for bootstrapping a new paxx project."""

import re
from pathlib import Path

import typer
from jinja2 import Environment, FileSystemLoader
from rich.console import Console

console = Console()


def get_templates_dir() -> Path:
    """Get the path to the templates directory."""
    return Path(__file__).parent.parent / "templates"


def to_snake_case(name: str) -> str:
    """Convert a string to snake_case."""
    # Replace hyphens with underscores
    name = name.replace("-", "_")
    # Insert underscore before uppercase letters and convert to lowercase
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    # Remove any non-alphanumeric characters except underscores
    name = re.sub(r"[^a-z0-9_]", "", name)
    return name


def validate_project_name(name: str) -> str:
    """Validate and normalize project name."""
    # Check it starts with a letter
    if not name[0].isalpha():
        raise typer.BadParameter("Project name must start with a letter")

    # Check for valid characters
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
        raise typer.BadParameter(
            "Project name can only contain letters, numbers, hyphens, and underscores"
        )

    return name


def create_project(
    name: str = typer.Argument(..., help="Name of the new project"),
    output_dir: Path = typer.Option(
        Path("."),
        "--output-dir",
        "-o",
        help="Directory to create the project in (default: current directory)",
    ),
    description: str = typer.Option(
        "",
        "--description",
        "-d",
        help="Project description",
    ),
    author: str = typer.Option(
        "Author",
        "--author",
        "-a",
        help="Author name",
    ),
) -> None:
    """Bootstrap a new paxx project.

    This command scaffolds a new FastAPI project following paxx conventions,
    including database setup, configuration, and the application factory pattern.

    Examples:
        paxx bootstrap myproject
        paxx bootstrap my-api --description "My awesome API"
        paxx bootstrap myproject -o /path/to/projects
    """
    # Validate name
    name = validate_project_name(name)
    snake_name = to_snake_case(name)

    # Create project directory
    project_dir = output_dir / name

    if project_dir.exists():
        console.print(f"[red]Error:[/red] Directory '{project_dir}' already exists")
        raise typer.Exit(1)

    console.print(f"Creating new paxx project: [bold cyan]{name}[/bold cyan]")

    # Set up Jinja environment
    templates_dir = get_templates_dir()
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        keep_trailing_newline=True,
    )

    # Template context
    context = {
        "project_name": name,
        "project_name_snake": snake_name,
        "project_description": description
        or "A FastAPI application built with paxx conventions",
        "author_name": author,
    }

    # Define project structure with templates
    project_files: dict[str, str | None] = {
        # Root files
        "pyproject.toml": "project/pyproject.toml.jinja",
        "settings.py": "project/settings.py.jinja",
        ".env.example": "project/.env.example.jinja",
        ".env": "project/.env.example.jinja",  # Create initial .env from example
        "alembic.ini": "project/alembic.ini.jinja",
        "main.py": "project/main.py.jinja",
        # Core module
        "core/__init__.py": "project/core/__init__.py.jinja",
        "core/exceptions.py": "project/core/exceptions.py.jinja",
        "core/middleware.py": "project/core/middleware.py.jinja",
        "core/dependencies.py": "project/core/dependencies.py.jinja",
        "core/schemas.py": "project/core/schemas.py.jinja",
        # Database module
        "db/__init__.py": "project/db/__init__.py.jinja",
        "db/database.py": "project/db/database.py.jinja",
        "db/migrations/env.py": "project/db/migrations/env.py.jinja",
        "db/migrations/script.py.mako": "project/db/migrations/script.py.mako.jinja",
        "db/migrations/versions/.gitkeep": None,  # Empty file
        # Features directory
        "features/.gitkeep": None,  # Empty file
        # Test fixtures
        "conftest.py": None,  # Pytest fixtures at root
    }

    # Create directories and files
    try:
        for file_path, template_name in project_files.items():
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            if template_name is None:
                # Create empty file or directory marker
                if file_path.endswith("conftest.py"):
                    full_path.write_text(_get_conftest_content())
                elif file_path.endswith("__init__.py"):
                    full_path.write_text('"""Test package."""\n')
                else:
                    full_path.touch()
            else:
                # Render template
                template = env.get_template(template_name)
                content = template.render(**context)
                full_path.write_text(content)

            console.print(f"  [green]Created[/green] {file_path}")

        # Create README
        readme_path = project_dir / "README.md"
        readme_path.write_text(_get_readme_content(name, description))
        console.print("  [green]Created[/green] README.md")

        # Create .gitignore
        gitignore_path = project_dir / ".gitignore"
        gitignore_path.write_text(_get_gitignore_content())
        console.print("  [green]Created[/green] .gitignore")

        console.print()
        console.print("[bold green]Project created successfully![/bold green]")
        console.print()
        console.print("Next steps:")
        console.print(f"  1. cd {name}")
        console.print("  2. uv sync --all-extras")
        console.print("  3. uv run paxx start")
        console.print()
        console.print("To create a new feature:")
        console.print("  uv run paxx feature create <feature_name>")

    except Exception as e:
        console.print(f"[red]Error creating project:[/red] {e}")
        raise typer.Exit(1) from None


def _get_conftest_content() -> str:
    """Get content for tests/conftest.py."""
    return '''"""Shared test fixtures."""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
async def client():
    """Async test client fixture."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
'''


def _get_readme_content(name: str, description: str) -> str:
    """Get content for README.md."""
    desc = description or "A FastAPI application built with paxx conventions"
    return f"""# {name}

{desc}

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Install dependencies
uv sync --all-extras

# Run the development server
uv run paxx start

# Or use uvicorn directly
uv run uvicorn main:feature --reload
```

### Database Migrations

```bash
# Create a new migration
uv run paxx db migrate "description"

# Apply migrations
uv run paxx db upgrade

# Revert last migration
uv run paxx db downgrade
```

### Creating Features

```bash
# Create a new domain feature
uv run paxx feature create users
```

## Project Structure

```
{name}/
├── main.py              # Application entry point
├── settings.py          # Configuration
├── conftest.py          # Pytest fixtures
├── alembic.ini          # Alembic configuration
├── core/                # Core utilities
│   ├── exceptions.py    # Custom exceptions
│   ├── middleware.py    # Custom middleware
│   ├── dependencies.py  # FastAPI dependencies
│   └── schemas.py       # Pydantic schemas
├── db/                  # Database
│   ├── database.py      # Database setup
│   └── migrations/      # Alembic migrations
└── features/            # Domain features
    └── <feature_name>/
        ├── models.py    # SQLAlchemy models
        ├── schemas.py   # Pydantic schemas
        ├── services.py  # Business logic
        └── routes.py    # API endpoints
```

## License

MIT
"""


def _get_gitignore_content() -> str:
    """Get content for .gitignore."""
    return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# Type checking
.mypy_cache/
.dmypy.json
dmypy.json

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
"""
