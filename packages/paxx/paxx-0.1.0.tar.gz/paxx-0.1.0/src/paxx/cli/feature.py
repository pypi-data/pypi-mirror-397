"""CLI subcommands for managing features."""

import ast
import re
import shutil
from pathlib import Path

import typer
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.table import Table

from paxx.features import get_feature_dir, list_available_features

app = typer.Typer(
    name="feature",
    help="Manage paxx features",
    no_args_is_help=True,
)

console = Console()


def _get_templates_dir() -> Path:
    """Get the path to the templates directory."""
    return Path(__file__).parent.parent / "templates"


def _to_snake_case(name: str) -> str:
    """Convert a string to snake_case."""
    # Replace hyphens with underscores
    name = name.replace("-", "_")
    # Insert underscore before uppercase letters and convert to lowercase
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    # Remove any non-alphanumeric characters except underscores
    name = re.sub(r"[^a-z0-9_]", "", name)
    return name


def _validate_feature_name(name: str) -> str:
    """Validate and normalize feature name."""
    # Check it starts with a letter
    if not name[0].isalpha():
        raise typer.BadParameter("Feature name must start with a letter")

    # Check for valid characters
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
        raise typer.BadParameter(
            "Feature name can only contain letters, numbers, hyphens, and underscores"
        )

    return _to_snake_case(name)


def _check_project_context() -> Path:
    """Check that we're in a paxx project directory.

    Returns:
        Path to the features directory.

    Raises:
        typer.Exit: If not in a valid project directory.
    """
    cwd = Path.cwd()

    # Check for key project files
    required_files = ["main.py", "settings.py"]
    missing = [f for f in required_files if not (cwd / f).exists()]

    if missing:
        console.print(
            "[red]Error:[/red] Not in a paxx project directory.\n"
            "Make sure you're running this command from your project root "
            "(where main.py and settings.py are located)."
        )
        raise typer.Exit(1)

    features_dir = cwd / "features"
    if not features_dir.exists():
        features_dir.mkdir(parents=True)

    return features_dir


def _list_features() -> None:
    """Display a table of available bundled features."""
    features = list_available_features()

    if not features:
        console.print("[yellow]No features available yet.[/yellow]")
        console.print(
            "\nFeature templates are coming soon. Check the documentation for updates."
        )
        return

    table = Table(title="Available Features")
    table.add_column("Feature", style="cyan")
    table.add_column("Description", style="white")

    # Feature descriptions
    descriptions = {
        "auth": "Authentication & user management",
        "admin": "Admin panel for managing models",
        "permissions": "Role-based access control (RBAC)",
        "example_products": "Example CRUD feature for product catalog",
    }

    for feature in features:
        description = descriptions.get(feature, "No description available")
        table.add_row(feature, description)

    console.print(table)
    console.print("\nUsage: [bold]uv run paxx feature add <feature>[/bold]")


def _get_feature_config(source_dir: Path) -> dict[str, str | list[str]]:
    """Extract feature configuration from config.py using AST parsing.

    Args:
        source_dir: Path to the feature source directory.

    Returns:
        Dict with 'prefix' and 'tags' from the feature config.
    """
    config_file = source_dir / "config.py"
    if not config_file.exists():
        return {"prefix": "", "tags": []}

    content = config_file.read_text()
    tree = ast.parse(content)

    prefix = ""
    tags: list[str] = []

    # Find the dataclass and extract default values
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not isinstance(item, ast.AnnAssign):
                continue
            if not isinstance(item.target, ast.Name):
                continue
            if item.target.id == "prefix" and isinstance(item.value, ast.Constant):
                prefix = item.value.value
            elif item.target.id == "tags" and isinstance(item.value, ast.Call):
                # Handle field(default_factory=lambda: ["tag"])
                for kw in item.value.keywords:
                    if (
                        kw.arg == "default_factory"
                        and isinstance(kw.value, ast.Lambda)
                        and isinstance(kw.value.body, ast.List)
                    ):
                        tags = [
                            elt.value
                            for elt in kw.value.body.elts
                            if isinstance(elt, ast.Constant)
                        ]

    return {"prefix": prefix, "tags": tags}


def _register_router_in_main(feature_name: str, prefix: str, tags: list[str]) -> bool:
    """Add router import and registration to main.py.

    Args:
        feature_name: Name of the feature (e.g., 'example_products').
        prefix: URL prefix for the router (e.g., '/products').
        tags: OpenAPI tags for the router.

    Returns:
        True if successful, False otherwise.
    """
    main_py = Path.cwd() / "main.py"
    if not main_py.exists():
        return False

    content = main_py.read_text()

    # Create the import alias from feature name
    # e.g., example_products -> example_products_router
    router_alias = f"{feature_name}_router"

    # Check if already registered
    if f"features.{feature_name}.routes" in content:
        console.print("  [yellow]Router already registered in main.py[/yellow]")
        return True

    # Build the import line
    import_line = f"from features.{feature_name}.routes import router as {router_alias}"

    # Build the include_router line
    tags_str = str(tags)
    include_line = (
        f'    app.include_router({router_alias}, prefix="{prefix}", tags={tags_str})'
    )

    # Find where to insert the import (after existing imports)
    lines = content.split("\n")
    new_lines = []
    import_inserted = False
    include_inserted = False

    for i, line in enumerate(lines):
        new_lines.append(line)

        # Insert import after the last 'from' import before the first function/class
        if not import_inserted:
            # Check if next non-empty line is a function or class definition
            next_significant = None
            for future_line in lines[i + 1 :]:
                stripped = future_line.strip()
                if stripped and not stripped.startswith("#"):
                    next_significant = stripped
                    break

            is_import_line = line.strip().startswith(("from ", "import "))
            is_before_code = next_significant and (
                next_significant.startswith(("@", "def ", "class ", '"""'))
                or next_significant == ""
            )
            has_next_line = i + 1 < len(lines)
            next_is_not_import = (
                has_next_line
                and not lines[i + 1].strip().startswith(("from ", "import "))
            )

            if is_import_line and is_before_code and next_is_not_import:
                new_lines.append(import_line)
                import_inserted = True

        # Insert include_router before 'return app' in create_app
        if not include_inserted and line.strip() == "return app":
            # Insert the include_router line before return feature
            new_lines.insert(-1, include_line)
            new_lines.insert(-1, "")
            include_inserted = True

    if not import_inserted or not include_inserted:
        return False

    main_py.write_text("\n".join(new_lines))
    return True


def _copy_feature(feature_name: str, source_dir: Path, target_dir: Path) -> None:
    """Copy a bundled feature to the project features directory.

    Args:
        feature_name: Name of the feature being copied.
        source_dir: Source directory (bundled feature).
        target_dir: Target directory (in features/).
    """
    files_copied = []

    for item in source_dir.iterdir():
        # Skip __pycache__ directories
        if item.name == "__pycache__":
            continue

        target_path = target_dir / item.name

        if item.is_file():
            shutil.copy2(item, target_path)
            files_copied.append(item.name)
        elif item.is_dir():
            # Recursively copy subdirectories
            shutil.copytree(
                item, target_path, ignore=shutil.ignore_patterns("__pycache__")
            )
            files_copied.append(f"{item.name}/")

    # Display copied files
    for file_name in sorted(files_copied):
        console.print(f"  [green]Created[/green] features/{feature_name}/{file_name}")


@app.command("add")
def add(
    feature: str = typer.Argument(
        None,
        help="Name of the feature to add (e.g., auth, admin, permissions)",
    ),
    list_: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all available features",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing feature if it exists",
    ),
) -> None:
    """Add a paxx bundled feature to your project.

    Features are pre-built templates that get copied into your features/
    directory. Once added, you own the code and can customize it freely.

    Examples:
        paxx feature add auth          # Add authentication system
        paxx feature add --list        # List available features
        paxx feature add auth --force  # Overwrite existing auth feature
    """
    # Handle --list flag
    if list_:
        _list_features()
        return

    # Require feature name if not listing
    if feature is None:
        console.print("[red]Error:[/red] Please specify a feature name.\n")
        _list_features()
        raise typer.Exit(1)

    # Validate we're in a project
    features_dir = _check_project_context()

    # Check if feature exists in bundled features
    available = list_available_features()
    source_dir = get_feature_dir(feature)

    if source_dir is None:
        console.print(f"[red]Error:[/red] Unknown feature '{feature}'.\n")
        if available:
            console.print("Available features:")
            for f in available:
                console.print(f"  - {f}")
        else:
            console.print("[yellow]No features are available yet.[/yellow]")
        raise typer.Exit(1)

    # Check if feature already exists in project
    target_dir = features_dir / feature

    if target_dir.exists():
        if force:
            console.print(
                f"[yellow]Warning:[/yellow] Overwriting existing feature '{feature}'"
            )
            shutil.rmtree(target_dir)
        else:
            console.print(
                f"[red]Error:[/red] Feature '{feature}' already exists.\n"
                "Use --force to overwrite."
            )
            raise typer.Exit(1)

    console.print(f"Adding feature: [bold cyan]{feature}[/bold cyan]")

    # Get feature configuration for router registration
    feature_config = _get_feature_config(source_dir)
    prefix = feature_config.get("prefix", f"/{feature.replace('_', '-')}")
    tags = feature_config.get("tags", [feature.replace("_", " ")])
    if not isinstance(tags, list):
        tags = [str(tags)]

    # Create target directory and copy files
    try:
        target_dir.mkdir(parents=True)
        _copy_feature(feature, source_dir, target_dir)

        # Register router in main.py
        if _register_router_in_main(feature, prefix, tags):
            console.print("  [green]Updated[/green] main.py")
        else:
            console.print(
                "  [yellow]Could not auto-register router in main.py[/yellow]"
            )
            console.print(
                f"  Add manually: app.include_router({feature}_router, "
                f'prefix="{prefix}", tags={tags})'
            )

        console.print()
        console.print("[bold green]Feature added successfully![/bold green]")
        console.print()
        console.print("Next steps:")
        console.print(f"  1. Review the code in features/{feature}/")
        console.print("  2. Customize as needed for your project")
        console.print("  3. Create and apply migrations:")
        console.print(f'     uv run paxx db migrate "add {feature}"')
        console.print("     uv run paxx db upgrade")

    except Exception as e:
        console.print(f"[red]Error adding feature:[/red] {e}")
        # Clean up on failure
        if target_dir.exists():
            shutil.rmtree(target_dir)
        raise typer.Exit(1) from None


@app.command("create")
def create(
    name: str = typer.Argument(..., help="Name of the new feature"),
    description: str = typer.Option(
        "",
        "--description",
        "-d",
        help="Feature description",
    ),
) -> None:
    """Create a new domain feature within the current paxx project.

    This command scaffolds a new feature in the features/ directory with the
    standard paxx feature structure: models, schemas, services, and routes.

    Examples:
        paxx feature create users
        paxx feature create blog_posts
        paxx feature create orders --description "Order management"
    """
    # Validate we're in a project
    features_dir = _check_project_context()

    # Validate and normalize feature name
    feature_name = _validate_feature_name(name)

    # Check if feature already exists
    feature_dir = features_dir / feature_name

    if feature_dir.exists():
        console.print(f"[red]Error:[/red] Feature '{feature_name}' already exists")
        raise typer.Exit(1)

    console.print(f"Creating new feature: [bold cyan]{feature_name}[/bold cyan]")

    # Set up Jinja environment
    templates_dir = _get_templates_dir()
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        keep_trailing_newline=True,
    )

    # Template context
    context = {
        "feature_name": feature_name,
        "feature_description": description,
    }

    # Define feature files with templates
    feature_files: dict[str, str] = {
        "__init__.py": "feature/__init__.py.jinja",
        "config.py": "feature/config.py.jinja",
        "models.py": "feature/models.py.jinja",
        "schemas.py": "feature/schemas.py.jinja",
        "services.py": "feature/services.py.jinja",
        "routes.py": "feature/routes.py.jinja",
    }

    # Create feature directory and files
    try:
        feature_dir.mkdir(parents=True)

        for file_name, template_name in feature_files.items():
            file_path = feature_dir / file_name
            template = env.get_template(template_name)
            content = template.render(**context)
            file_path.write_text(content)
            console.print(
                f"  [green]Created[/green] features/{feature_name}/{file_name}"
            )

        console.print()
        console.print("[bold green]Feature created successfully![/bold green]")
        console.print()
        console.print("Next steps:")
        console.print(f"  1. Define your models in features/{feature_name}/models.py")
        console.print(f"  2. Create schemas in features/{feature_name}/schemas.py")
        console.print(
            f"  3. Implement business logic in features/{feature_name}/services.py"
        )
        console.print(f"  4. Add routes in features/{feature_name}/routes.py")
        console.print()
        console.print("Then create and apply migrations:")
        console.print(f'  uv run paxx db migrate "add {feature_name} models"')
        console.print("  uv run paxx db upgrade")

    except Exception as e:
        console.print(f"[red]Error creating feature:[/red] {e}")
        raise typer.Exit(1) from None
