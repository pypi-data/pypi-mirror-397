# src/scaffold/generator.py
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Create a single Console instance to use throughout the file
console = Console()

def create_project(project_name: str, template_name: str = "basic", target_dir: str = "."):
    """
    Generates a new Python project from a specified template.
    """
    template_path = os.path.join(os.path.dirname(__file__), "templates", template_name)
    if not os.path.exists(template_path):
        raise ValueError(f"Template '{template_name}' not found at {template_path}")

    env = Environment(
        loader=FileSystemLoader(template_path),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True
    )
    env.filters['slugify'] = lambda value: value.lower().replace(" ", "_").replace("-", "_")

    project_path = os.path.join(target_dir, project_name)
    src_path = os.path.join(project_path, "src", project_name.replace("-", "_"))

    # Use a rich Progress context manager
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True, # Remove the progress bar when it's done
    ) as progress:
        # Create directories
        task1 = progress.add_task(f"Creating project directory: {project_path}", total=1)
        os.makedirs(project_path, exist_ok=True)
        progress.update(task1, advance=1)

        task2 = progress.add_task(f"Creating source directory: {src_path}", total=1)
        os.makedirs(src_path, exist_ok=True)
        progress.update(task2, advance=1)

        # Render and write files
        render_and_write(progress, env, "pyproject.toml.j2", project_path, "pyproject.toml", project_name=project_name)
        render_and_write(progress, env, "README.md.j2", project_path, "README.md", project_name=project_name)
        render_and_write(progress, env, ".gitignore.j2", project_path, ".gitignore", project_name=project_name)

        if os.path.exists(os.path.join(template_path, "main.py.j2")):
            render_and_write(progress, env, "main.py.j2", src_path, "main.py", project_name=project_name)
        
        with open(os.path.join(src_path, "__init__.py"), "w") as f:
            f.write("")
        console.print(f"✅ Created file: {os.path.join(src_path, '__init__.py')}", style="bold green")


def render_and_write(progress, env: Environment, template_name: str, output_path: str, output_filename: str, **context):
    """
    Helper function to render a template and write it to a file, with a progress update.
    """
    task = progress.add_task(f"Creating file: {output_filename}", total=1)
    template = env.get_template(template_name)
    rendered_content = template.render(**context)
    filepath = os.path.join(output_path, output_filename)
    with open(filepath, "w") as f:
        f.write(rendered_content)
    progress.update(task, advance=1)
    # We'll let the progress spinner show the file creation, so no print here