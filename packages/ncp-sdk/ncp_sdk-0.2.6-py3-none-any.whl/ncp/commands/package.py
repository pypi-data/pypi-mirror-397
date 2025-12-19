"""Project packaging command."""

import tarfile
import tempfile
import shutil
from pathlib import Path
import re
import click
import pathspec
import toml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()


# Default patterns to always exclude from packages
DEFAULT_EXCLUDES = [
    # Version control
    ".git/",
    ".gitignore",
    ".gitattributes",

    # Python bytecode and compiled files
    "__pycache__/",
    "*.py[cod]",
    "*$py.class",
    "*.so",
    "*.dylib",

    # Virtual environments
    "venv/",
    ".venv/",
    "env/",
    "ENV/",
    ".virtualenv/",

    # Environment and secrets
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "credentials.json",

    # IDE and editors
    ".vscode/",
    ".idea/",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",

    # Build and distribution
    "dist/",
    "build/",
    "*.egg-info/",
    "*.egg",

    # Testing and coverage
    ".pytest_cache/",
    ".coverage",
    ".tox/",
    "htmlcov/",
    ".mypy_cache/",

    # Package files (don't package existing .ncp files)
    "*.ncp",

    # Jupyter
    ".ipynb_checkpoints/",
]


def sanitize_package_name(name: str) -> str:
    """Validate and sanitize a package name for filesystem safety.

    Args:
        name: The package name to validate

    Returns:
        The sanitized package name

    Raises:
        ValueError: If the name is invalid or unsafe
    """
    if not name or not name.strip():
        raise ValueError("Package name cannot be empty")

    # Check for invalid filesystem characters
    invalid_chars = r'[/\\:*?"<>|]'
    if re.search(invalid_chars, name):
        raise ValueError(
            f"Package name contains invalid characters. "
            f"Avoid: / \\ : * ? \" < > |"
        )

    # Trim whitespace
    name = name.strip()

    # Check for reserved names on Windows
    reserved_names = {
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    }
    if name.upper() in reserved_names:
        raise ValueError(f"Package name '{name}' is a reserved system name")

    return name


def load_ignore_spec(project_dir: Path) -> pathspec.GitIgnoreSpec:
    """Load ignore patterns from .ncpignore and defaults.

    Args:
        project_dir: Path to the project directory

    Returns:
        GitIgnoreSpec with combined patterns from defaults and .ncpignore
    """
    patterns = DEFAULT_EXCLUDES.copy()

    # Check if .ncpignore exists and load additional patterns
    ncpignore_file = project_dir / ".ncpignore"
    if ncpignore_file.exists():
        try:
            with open(ncpignore_file, "r") as f:
                # Read non-empty, non-comment lines
                user_patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith("#")
                ]
                patterns.extend(user_patterns)
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Warning: Could not read .ncpignore: {e}")

    return pathspec.GitIgnoreSpec.from_lines(patterns)


def package_project(project_path: str, output: str = None, version: str = None):
    """Package an agent project for deployment.

    Args:
        project_path: Path to the project directory
        output: Output file path (optional)
        version: Version tag (optional)
    """
    project_dir = Path(project_path).resolve()

    # Validate project exists
    if not project_dir.exists():
        console.print()
        console.print(f"[red]✗[/red] Project directory not found: {project_dir}")
        console.print()
        raise click.Abort()

    # Read project name from ncp.toml
    toml_file = project_dir / "ncp.toml"
    if not toml_file.exists():
        console.print()
        console.print(f"[red]✗[/red] ncp.toml not found in {project_dir}")
        console.print()
        raise click.Abort()

    try:
        config = toml.load(toml_file)
        project_name = config.get("project", {}).get("name")
        if not project_name:
            console.print()
            console.print("[red]✗[/red] Project name not found in ncp.toml [project] section")
            console.print()
            raise click.Abort()

        # Validate and sanitize the project name
        project_name = sanitize_package_name(project_name)
    except ValueError as e:
        console.print()
        console.print(f"[red]✗[/red] Invalid project name in ncp.toml: {e}")
        console.print()
        raise click.Abort()
    except Exception as e:
        console.print()
        console.print(f"[red]✗[/red] Error reading ncp.toml: {e}")
        console.print()
        raise click.Abort()

    # Determine output filename
    if output:
        output_file = Path(output)
    else:
        output_file = Path.cwd() / f"{project_name}.ncp"

    console.print()
    console.print(f"[cyan]Packaging:[/cyan] {project_name}")
    console.print()

    try:
        # Load ignore patterns
        ignore_spec = load_ignore_spec(project_dir)

        # Create temporary directory for staging
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            package_root = temp_path / project_name

            # Copy files to staging area
            files_included = []

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Collecting files...", total=None)

                # Collect all files recursively, excluding ignored patterns
                for src_file in project_dir.rglob("*"):
                    if src_file.is_file():
                        relative_path = src_file.relative_to(project_dir)
                        # Check if file should be excluded
                        if not ignore_spec.match_file(str(relative_path)):
                            dst_file = package_root / relative_path
                            dst_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(src_file, dst_file)
                            files_included.append(relative_path)

            if not files_included:
                console.print()
                console.print("[red]✗[/red] No files to package")
                console.print()
                raise click.Abort()

            # Show collected files
            console.print("[dim]Files collected:[/dim]")
            for f in files_included[:5]:  # Show first 5
                console.print(f"  [green]✓[/green] {f}")
            if len(files_included) > 5:
                console.print(f"  [dim]... and {len(files_included) - 5} more[/dim]")
            console.print()

            # Create archive
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Creating package archive...", total=None)
                with tarfile.open(output_file, "w:gz") as tar:
                    tar.add(package_root, arcname=project_name)

            # Get file size
            file_size = output_file.stat().st_size
            size_kb = file_size / 1024
            size_display = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"

            # Success message
            success_text = f"[green]Package:[/green] {output_file.name}\n"
            success_text += f"[green]Size:[/green]    {size_display}\n"
            success_text += f"[green]Files:[/green]   {len(files_included)}\n\n"
            success_text += f"[dim]Deploy your agent:[/dim]\n"
            success_text += f"  [cyan]ncp deploy {output_file.name}[/cyan]"

            console.print(Panel(
                success_text,
                title="[bold green]✓ Package Ready for Deployment[/bold green]",
                border_style="green"
            ))
            console.print()

    except Exception as e:
        console.print()
        console.print(f"[red]✗[/red] Error packaging project: {e}")
        console.print()
        if output_file.exists():
            output_file.unlink()
        raise click.Abort()
