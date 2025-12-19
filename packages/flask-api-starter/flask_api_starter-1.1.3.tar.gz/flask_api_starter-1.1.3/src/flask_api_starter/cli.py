import click
import shutil
from importlib.resources import files
import os
from pathlib import Path

@click.group()
def cli():
    """Flask API Starter Kit CLI"""
    pass

@cli.command()
@click.argument("project_name")
def new(project_name):
    """Generate a new Flask API project from bundled template."""

    # Try to load the template from the installed package
    template_path = None
    try:
        template_path = files("flask_api_starter").joinpath("templates")
    except Exception:
        pass

    # Fallback for development (local repo)
    if template_path is None or not template_path.exists():
        template_path = Path(os.path.dirname(__file__)) / "templates"

    if not template_path.exists():
        raise click.ClickException(f"Template directory not found: {template_path}")

    # Destination folder
    dest = Path.cwd() / project_name
    if dest.exists():
        click.echo(f"Destination {dest} already exists. Aborting.")
        return

    # Copy template files
    shutil.copytree(template_path, dest)

    click.echo(f"Project created at ./{project_name}")
    click.echo("Next steps:")
    click.echo(f"  cd {project_name}")
    click.echo(f"  create a virtual environment")
    click.echo("  pip install -r requirements.txt")
    click.echo("  python run.py")
