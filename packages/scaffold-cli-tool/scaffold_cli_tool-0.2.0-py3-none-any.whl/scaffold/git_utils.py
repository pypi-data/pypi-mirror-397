# src/scaffold/git_utils.py
import os
from git import Repo
from rich.console import Console

console = Console()

def initialize_git_repo(project_path: str):
    """
    Initializes a git repository, adds all files, and makes an initial commit.
    """
    try:
        console.print("\n🔧 Initializing Git repository...", style="bold blue")
        
        # 1. Initialize the repository
        repo = Repo.init(project_path)
        
        # 2. Add all files to the staging area
        repo.git.add(all=True)
        
        # 3. Create the initial commit
        repo.index.commit("Initial commit from Scaffold")
        
        console.print("✅ Git repository initialized with initial commit.", style="bold green")

    except Exception as e:
        console.print(f"[bold red]Error initializing git repository:[/bold red] {e}", style="bold red")
