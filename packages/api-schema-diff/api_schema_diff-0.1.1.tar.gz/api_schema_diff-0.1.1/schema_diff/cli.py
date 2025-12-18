import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .diff import diff_objects
from .loader import load_schema, SchemaKind
from .models import DiffResult
from .openapi.diff import diff_openapi

app = typer.Typer(add_completion=False)
console = Console()


def version_callback(value: bool):
    """Callback for --version flag."""
    if value:
        try:
            from importlib.metadata import version
            pkg_version = version("api-schema-diff")
        except Exception:
            pkg_version = "0.1.0"  # fallback version
        console.print(f"api-schema-diff version {pkg_version}")
        raise typer.Exit()


@app.command()
def main(
    old_file: Path = typer.Argument(
        ..., exists=True, readable=True, help="Old schema/file (JSON or YAML)"
    ),
    new_file: Path = typer.Argument(
        ..., exists=True, readable=True, help="New schema/file (JSON or YAML)"
    ),
    format: str = typer.Option("text", "--format", help="Output format: text|json"),
    fail_on_breaking: bool = typer.Option(
        True,
        "--fail-on-breaking/--no-fail-on-breaking",
        help="Exit with code 1 when breaking changes are found (default: true).",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
):
    """
    api-schema-diff

    Exit code (default):
      0 -> no breaking changes
      1 -> breaking changes found

    With --no-fail-on-breaking:
      always exits 0 (report-only mode)
    """
    old_loaded = load_schema(old_file)
    new_loaded = load_schema(new_file)

    if format.lower() != "json":
        console.print(
            f"[dim]Old schema:[/dim] {old_loaded.kind.value}  "
            f"[dim]New schema:[/dim] {new_loaded.kind.value}"
        )

    if old_loaded.kind == SchemaKind.OPENAPI and new_loaded.kind == SchemaKind.OPENAPI:
        result: DiffResult = diff_openapi(old_loaded.raw, new_loaded.raw)
    else:
        result = diff_objects(old_loaded.raw, new_loaded.raw)

    exit_code = result.exit_code()
    if not fail_on_breaking:
        exit_code = 0

    if format.lower() == "json":
        console.print_json(json.dumps(result.to_dict()))
        raise typer.Exit(code=exit_code)

    if result.has_breaking_changes():
        console.print("\n[bold red]BREAKING CHANGES FOUND[/bold red]\n")
        t = Table(show_header=True, header_style="bold red")
        t.add_column("Type")
        t.add_column("Path")
        t.add_column("Old Type")
        t.add_column("New Type")
        t.add_column("Message")
        for c in result.breaking:
            t.add_row(
                c.change_type.value,
                c.path,
                c.old_type or "",
                c.new_type or "",
                c.message or "",
            )
        console.print(t)
    else:
        console.print("\n[bold green]No breaking changes found.[/bold green]")

    if result.non_breaking:
        console.print("\n[bold]Non-breaking changes:[/bold]")
        t2 = Table(show_header=True, header_style="bold")
        t2.add_column("Type")
        t2.add_column("Path")
        t2.add_column("Message")
        for c in result.non_breaking:
            t2.add_row(c.change_type.value, c.path, c.message or "")
        console.print(t2)

    raise typer.Exit(code=exit_code)


if __name__ == "__main__":
    app()
