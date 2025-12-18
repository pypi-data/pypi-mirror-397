import typer
from rich.console import Console # allows us to create a console instance
from rich.panel import Panel # allows us to create a panel instance
from rich.prompt import Prompt # allows us to create a prompt instance
import sys
import os
from .config import get_api_key, GIT_INTERVIEWER_MODE
from git_interviewer.git_utils import get_staged_diff, install_hook
from .llm import generate_question
from .personas import PERSONAS



# app = typer.Typer() # initialization of core CLI app, returns a callable object
app = typer.Typer(
    rich_markup_mode="rich"
)
console = Console()


@app.callback()
def main(ctx: typer.Context):
    """
    [bold blue]Git Interviewer 🎤[/bold blue]

    A pre-commit hook that acts as a technical interviewer.
    It blocks your commits until you answer a question about your code changes.

    [bold]Usage:[/bold]
    
    1. Initialize in a repo: [green]git-interviewer init[/green]
    2. Commit normally: [green]git commit -m "..."[/green]
    
    [bold]Configuration:[/bold]
    
    Set [cyan]GEMINI_API_KEY[/cyan] and [cyan]GIT_INTERVIEWER_MODE[/cyan] env vars.

    [bold]Bypass:[/bold]
    
    To skip the interview, use: [yellow]git commit --no-verify[/yellow]
    """
    pass


@app.command() # decorator to register the function as a CLI command
def init(): 
    """ install the git interviewer pre commit hook """
    install_hook()
    
@app.command()
def interview(): 
    """ Analyse staged changes and interview the developer """
    
    # 1. CHECK API KEY FIRST
    api_key = get_api_key()
    if not api_key: 
        console.print("[yellow]⚠️  Git Interviewer skipped: GEMINI_API_KEY not found.[/yellow]")
        console.print("   To enable, run: [bold]export GEMINI_API_KEY='your_key'[/bold]")
        
        # exit code 0 so that the commit proceeds even without the interview. s
        raise typer.Exit(code=0)
    
    
    # 2. get diff
    diff = get_staged_diff()
    
    if not diff: 
        # no staged changes or empty diff
        # git handles this naturally i think
        return
    
    console.print(f"[bold blue] 🎤 Git Interviewer ({GIT_INTERVIEWER_MODE} mode) [/bold blue]")
    console.print(f"[bold green] Analyzing changes... [/bold green]", style="dim")
    
    try: 
        question = generate_question(diff)
        
    except Exception as e: 
        console.print(f"[red] Error connecting to AI:[/red] {e}")
        # fail open
        raise typer.Exit(code=0)
    
    console.print(Panel(question, title="Interviewer", border_style="blue"))
    
    # We cannot use Prompt.ask() directly because git hooks often have detached stdin.
    # We must explicitly read from /dev/tty to get user input.
    try:
        # We need to print the prompt to the console, but read from TTY
        console.print("[bold]Your Answer: [/bold]", end="")
        with open("/dev/tty", "r") as tty:
            answer = tty.readline().strip()
    except OSError:
        # Fallback if /dev/tty is not available (e.g. CI environments)
        console.print("[yellow]Warning: Cannot access terminal for input. Skipping interview.[/yellow]")
        raise typer.Exit(code=0)
    
    # validation: 
    if len(answer.split()) < 3: 
        console.print("[bold red]❌ That answer is too short! Commit rejected.[/bold red]")
        console.print("Please provide a meaningful explanation.")
        # exit code 1, do not allow commit. 
        raise typer.Exit(code=1)
    
    # want to implement back and forth with AI until AI likes all the answers. for now, just 
    # a question with an answer is good enough, no need to actually look at the answer
    console.print("[bold green]Good answer, commit allowed[/bold green]")
    raise typer.Exit(code=0)


@app.command()
def help(): 
    """ Display help information """
    console.print(Panel(
        "Git Interviewer is a pre-commit hook that interviews you about your code before letting you commit.",
        title="Git Interviewer",
        border_style="blue"
    ))
    
    console.print("Commands:")
    console.print("  init      Install the pre-commit hook")
    console.print("  interview Analyze staged changes and interview the developer")
    console.print("  help      Display help information")
    console.print("  version   Display version information")
    console.print("  --no-verify   append this to your git commit -m "" message to bypass git-interviewer")
    
    
    console.print("\nFor more details, see the documentation at [link]https://github.com/yourusername/git-interviewer[/link]")
    
    
@app.command()
def mode(
    name: str = typer.Argument(None, help="The name of the persona to switch to."),
    list_modes: bool = typer.Option(False, "--list", "-l", help="List available personas.")
):
    """
    View or set the interviewer persona.
    """
    if list_modes or name is None:
        console.print("[bold]Available Modes:[/bold]")
        for mode_name, description in PERSONAS.items():
            current_marker = " (current)" if mode_name == GIT_INTERVIEWER_MODE else ""
            console.print(f"- [green]{mode_name}[/green]{current_marker}: {description[:60]}...")
        return

    if name not in PERSONAS:
        console.print(f"[red]Error:[/red] Mode '{name}' not found.")
        console.print("Available modes: " + ", ".join(PERSONAS.keys()))
        raise typer.Exit(code=1)

    # Write to git config
    try:
        import subprocess
        subprocess.run(
            ["git", "config", "git-interviewer.mode", name],
            check=True
        )
        console.print(f"[green]✅ Switched to mode: {name}[/green] (saved to git config)")
    except subprocess.CalledProcessError:
        console.print("[red]Error:[/red] Failed to update git config.")
        raise typer.Exit(code=1)
    
@app.command()
def version(): 
    """ Display version information """
    from . import __version__
    console.print(f"[bold green]Git Interviewer v{__version__}[/bold green]")
    


