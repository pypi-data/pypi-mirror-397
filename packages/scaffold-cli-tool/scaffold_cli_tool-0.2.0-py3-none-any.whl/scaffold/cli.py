# src/scaffold/cli.py
import click
import os
from rich.console import Console
from .generator import create_project
from .git_utils import initialize_git_repo

# Create a Console instance
console = Console()

@click.group()
def cli():
    """A simple CLI tool to scaffold new Python projects."""
    pass

@cli.command()
@click.argument('project_name')
@click.option(
    '--template', 
    default='basic', 
    help='The project template to use (e.g., basic, fastapi).',
    type=click.Choice(['basic', 'fastapi'], case_sensitive=False)
)
@click.option(
    '--git', 
    is_flag=True,
    default=False,
    help='Initialize a git repository and make an initial commit.'
)
def create(project_name, template, git): # <-- Add 'git' here
    """Creates a new Python project."""
    console.print(f"🚀 Creating project '[bold cyan]{project_name}[/bold cyan]' with template '[bold magenta]{template}[/bold magenta]'...")
    
    output_dir = os.getcwd()
    project_path = os.path.join(output_dir, project_name)
    
    try:
        create_project(project_name, template_name=template, target_dir=output_dir)
        
        console.print("\n✨ [bold green]Project created successfully![/bold green] ✨\n")
        console.print("[bold]Next steps:[/bold]")
        console.print(f"  1. [dim]cd[/dim] [cyan]{project_name}[/cyan]")
        console.print(f"  2. [dim]python -m venv .venv[/dim]")
        console.print(f"  3. [dim].venv\\Scripts\\Activate[/dim]")
        console.print(f"  4. [dim]pip install -e .[/dim]")
        
        if template == 'fastapi':
            console.print(f"  5. [dim]uvicorn {project_name.replace('-', '_')}.main:app --reload[/dim]")
        else:
            console.print(f"  5. [dim]python -m {project_name.replace('-', '_')}.main[/dim]")

        # NEW: Call the git function if the flag is set
        if git:
            initialize_git_repo(project_path)

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("Try running 'scaffold create --help' to see available templates.")

if __name__ == '__main__':
    cli()