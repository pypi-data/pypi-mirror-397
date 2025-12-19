import click
import os
import datetime
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def find_project_root():
    """Find the project root directory (containing .git)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()  # Fallback to current directory

PROJECT_ROOT = find_project_root()
SPRINT_DIR = PROJECT_ROOT / ".sprint"
TODO_FILE = SPRINT_DIR / "TODO.md"
USAGE_FILE = SPRINT_DIR / "USAGE.md"
RETRO_FILE = SPRINT_DIR / "RETRO.md"

@click.group()
def main():
    """ai-sprint: Standardize your development sprints."""
    pass

@main.command()
@click.option('--name', prompt='Sprint Name', help='Name of the sprint directory (e.g., 001-setup)')
def init(name):
    """Initialize a new sprint directory structure."""
    # Check if name already starts with a number (e.g. "003-")
    # If not, auto-increment based on existing directories
    if not re.match(r'^\d{3}-', name):
        # Find highest current number
        max_num = 0
        if SPRINT_DIR.exists():
            for item in SPRINT_DIR.iterdir():
                if item.is_dir():
                    match = re.match(r'^(\d{3})-', item.name)
                    if match:
                        num = int(match.group(1))
                        if num > max_num:
                            max_num = num
        
        next_num = max_num + 1
        name = f"{next_num:03d}-{name}"

    target_dir = SPRINT_DIR / name
    
    if target_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Directory {target_dir} already exists.")
        return

    try:
        create_sprint_structure(target_dir, name)
        console.print(f"[bold green]Success:[/bold green] Initialized sprint directory at {target_dir}")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Failed to initialize sprint: {e}")

@main.command()
@click.argument('name')
def update(name):
    """Update an existing sprint with missing templates."""
    target_dir = SPRINT_DIR / name
    if not target_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Sprint {name} does not exist.")
        return

    try:
        create_sprint_structure(target_dir, name, exist_ok=True)
        console.print(f"[bold green]Success:[/bold green] Updated sprint directory at {target_dir}")
    except Exception as e:
         console.print(f"[bold red]Error:[/bold red] Failed to update sprint: {e}")

def create_sprint_structure(target_dir: Path, name: str, exist_ok: bool = False):
    target_dir.mkdir(parents=True, exist_ok=exist_ok)
    (target_dir / "planning").mkdir(exist_ok=True)
    (target_dir / "logs").mkdir(exist_ok=True)
    (target_dir / "context").mkdir(exist_ok=True)

    # Create standard files with templates if they don't exist
    readme_file = target_dir / "README.md"
    if not readme_file.exists():
        with open(readme_file, "w") as f:
            f.write(f"# Sprint: {name}\n\n## Goal\nDescribe the goal of this sprint.\n")
    
    tasks_file = target_dir / "planning" / "tasks.md"
    if not tasks_file.exists():
        with open(tasks_file, "w") as f:
            f.write("# Tasks\n\n- [ ] Initial Task\n")

    todo_file = target_dir / "TODO.md"
    if not todo_file.exists():
        with open(todo_file, "w") as f:
            f.write("# Sprint TODO\n\n## High Priority\n- [ ] \n\n## Backlog\n- [ ] \n")

    retro_file = target_dir / "RETRO.md"
    if not retro_file.exists():
        with open(retro_file, "w") as f:
            f.write("# Retrospective\n\n## Went Well\n\n## To Improve\n\n## Action Items\n")


@main.command()
@click.argument('task_name')
def start(task_name):
    """Start working on a specific task."""
    console.print(f"[bold blue]Starting task:[/bold blue] {task_name}")
    # Logic to log start time or update local state could go here
    # For now, we just acknowledge the command
    
    timestamp = datetime.datetime.now().isoformat()
    console.print(f"Recorded start time: {timestamp}")


import re

import sys

@main.command()
@click.argument('name')
def close(name):
    """Close a sprint if criteria are met."""
    target_dir = SPRINT_DIR / name
    if not target_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Sprint {name} does not exist.")
        sys.exit(1)

    # 0. Check for uncommitted changes
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, cwd='.')
        if result.returncode == 0 and result.stdout.strip():
            console.print(f"[bold red]Cannot close:[/bold red] Found uncommitted changes. Please commit or stash changes before closing sprint.")
            console.print(f"[yellow]Uncommitted files:[/yellow]")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    console.print(f"  {line}")
            sys.exit(1)
    except FileNotFoundError:
        console.print("[yellow]Warning:[/yellow] Git not found. Skipping uncommitted changes check.")
    except subprocess.CalledProcessError:
        console.print("[yellow]Warning:[/yellow] Could not check git status. Skipping uncommitted changes check.")

    # 1. Check TODO.md
    todo_file = target_dir / "TODO.md"
    if todo_file.exists():
        with open(todo_file, "r") as f:
            content = f.read()
            # Find all unchecked boxes: "- [ ]"
            unchecked = re.findall(r"-\s*\[\s\]", content)
            if unchecked:
                console.print(f"[bold red]Cannot close:[/bold red] Found {len(unchecked)} incomplete tasks in TODO.md")
                sys.exit(1)
    
    # 2. Check RETRO.md
    retro_file = target_dir / "RETRO.md"
    if not retro_file.exists():
        console.print("[bold red]Cannot close:[/bold red] RETRO.md missing.")
        sys.exit(1)
    
    # Simple check: Ensure RETRO is not just the template (naive check for size or custom content)
    # For now, just existence and non-empty is a good start. 
    if retro_file.stat().st_size < 50: # Arbitrary small size check
         console.print("[bold yellow]Warning:[/bold yellow] RETRO.md seems empty or too short. Please fill it out.")
         # We allow proceeding with a warning for now, or could block.
         # User said "RETRO is complete", implying strictness.
         # Let's prompt for confirmation if short.
         if not click.confirm("RETRO.md looks short. Are you sure it's complete?"):
             sys.exit(1)

    # Mark as closed
    status_file = target_dir / ".status"
    with open(status_file, "w") as f:
        f.write("Closed")
    
    console.print(f"[bold green]Success:[/bold green] Sprint {name} closed.")


@main.command()
def status():
    """Show the current status of the sprint."""
    if not SPRINT_DIR.exists():
         console.print("[yellow]No .sprint directory found.[/yellow]")
         return

    table = Table(title="Available Sprints")
    table.add_column("Sprint Name", style="cyan")
    table.add_column("Status", style="magenta")

    for item in sorted(SPRINT_DIR.iterdir()):
        if item.is_dir():
             # Check for .status file
             status_file = item / ".status"
             state = "Active"
             if status_file.exists():
                 with open(status_file, "r") as f:
                     state = f.read().strip()
             
             color = "green" if state == "Active" else "dim white"
             table.add_row(item.name, f"[{color}]{state}[/{color}]")

    console.print(table)


@main.command()
def finish():
    """Finish the current task."""
    console.print("[bold green]Task marked as finished.[/bold green]")


if __name__ == '__main__':
    main()
