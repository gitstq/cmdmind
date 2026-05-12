"""
CmdMind CLI Entry Point
Command-line interface for CmdMind
"""

import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint

from cmdmind import __version__
from cmdmind.core.database import CommandDatabase, Command
from cmdmind.core.classifier import CommandClassifier
from cmdmind.core.searcher import CommandSearcher
from cmdmind.core.analyzer import CommandAnalyzer

app = typer.Typer(
    name="cmdmind",
    help="🧠 AI-Powered Terminal Command Intelligence - Smart command history management",
    add_completion=False,
)

console = Console()


def get_db() -> CommandDatabase:
    """Get database instance"""
    return CommandDatabase()


@app.command()
def version():
    """Show version information"""
    console.print(f"[bold blue]CmdMind[/bold blue] version [green]{__version__}[/green]")


@app.command()
def add(
    command: str = typer.Argument(..., help="Command to add"),
    shell: str = typer.Option("bash", "--shell", "-s", help="Shell type"),
    cwd: str = typer.Option("", "--cwd", "-c", help="Working directory"),
    exit_code: int = typer.Option(0, "--exit-code", "-e", help="Exit code"),
    description: str = typer.Option("", "--desc", "-d", help="Command description"),
):
    """Add a command to history"""
    db = get_db()
    classifier = CommandClassifier()
    
    # Auto-classify
    category, confidence = classifier.classify(command)
    tags = classifier.extract_tags(command)
    
    if not description:
        description = classifier.suggest_description(command, category)
    
    cmd = Command(
        command=command,
        shell=shell,
        exit_code=exit_code,
        cwd=cwd,
        category=category,
        description=description,
        tags=tags,
    )
    
    cmd_id = db.add_command(cmd)
    
    console.print(f"[green]✓[/green] Added command #{cmd_id}")
    console.print(f"  Category: [blue]{category}[/blue] (confidence: {confidence:.0%})")
    if tags:
        console.print(f"  Tags: {', '.join(tags)}")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of results"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    favorites: bool = typer.Option(False, "--favorites", "-f", help="Search favorites only"),
):
    """Search command history"""
    db = get_db()
    searcher = CommandSearcher(db)
    
    results = searcher.search(
        query=query,
        limit=limit,
        category=category,
        favorites_only=favorites
    )
    
    if not results:
        console.print("[yellow]No commands found matching your query.[/yellow]")
        return
    
    table = Table(title=f"Search Results for '{query}'")
    table.add_column("#", style="dim", width=4)
    table.add_column("Command", style="cyan")
    table.add_column("Category", style="green", width=10)
    table.add_column("Score", style="yellow", width=6)
    table.add_column("Type", style="blue", width=8)
    
    for i, result in enumerate(results, 1):
        cmd = result.command
        table.add_row(
            str(i),
            cmd.command[:50] + ("..." if len(cmd.command) > 50 else ""),
            cmd.category,
            f"{result.score:.0%}",
            result.match_type
        )
    
    console.print(table)


@app.command()
def list(
    limit: int = typer.Option(30, "--limit", "-l", help="Number of commands to show"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
):
    """List recent commands"""
    db = get_db()
    
    if category:
        commands = db.get_by_category(category)
    else:
        commands = db.get_recent_commands(limit)
    
    if not commands:
        console.print("[yellow]No commands found.[/yellow]")
        return
    
    table = Table(title="Recent Commands")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Command", style="cyan")
    table.add_column("Category", style="green", width=10)
    table.add_column("Time", style="yellow", width=16)
    table.add_column("★", style="red", width=1)
    
    for cmd in commands[:limit]:
        time_str = cmd.timestamp.strftime("%m/%d %H:%M") if cmd.timestamp else ""
        fav = "★" if cmd.favorite else ""
        table.add_row(
            str(cmd.id),
            cmd.command[:45] + ("..." if len(cmd.command) > 45 else ""),
            cmd.category,
            time_str,
            fav
        )
    
    console.print(table)


@app.command()
def show(
    command_id: int = typer.Argument(..., help="Command ID to show"),
):
    """Show detailed information about a command"""
    db = get_db()
    cmd = db.get_command(command_id)
    
    if not cmd:
        console.print(f"[red]Command #{command_id} not found.[/red]")
        raise typer.Exit(1)
    
    # Display command details
    console.print(Panel(
        Syntax(cmd.command, "bash", theme="monokai", line_numbers=False),
        title=f"Command #{cmd.id}",
        border_style="blue"
    ))
    
    info_table = Table.grid(padding=(0, 2))
    info_table.add_column("Key", style="bold")
    info_table.add_column("Value")
    
    info_table.add_row("Category:", cmd.category)
    info_table.add_row("Shell:", cmd.shell)
    info_table.add_row("Exit Code:", str(cmd.exit_code))
    info_table.add_row("Working Dir:", cmd.cwd or "N/A")
    info_table.add_row("Timestamp:", cmd.timestamp.strftime("%Y-%m-%d %H:%M:%S") if cmd.timestamp else "N/A")
    info_table.add_row("Use Count:", str(cmd.use_count))
    info_table.add_row("Favorite:", "★ Yes" if cmd.favorite else "No")
    info_table.add_row("Tags:", ", ".join(cmd.tags) if cmd.tags else "None")
    info_table.add_row("Description:", cmd.description or "N/A")
    
    console.print(info_table)


@app.command()
def favorite(
    command_id: int = typer.Argument(..., help="Command ID to favorite/unfavorite"),
    remove: bool = typer.Option(False, "--remove", "-r", help="Remove from favorites"),
):
    """Toggle favorite status for a command"""
    db = get_db()
    cmd = db.get_command(command_id)
    
    if not cmd:
        console.print(f"[red]Command #{command_id} not found.[/red]")
        raise typer.Exit(1)
    
    cmd.favorite = not remove
    db.update_command(cmd)
    
    status = "removed from" if remove else "added to"
    console.print(f"[green]✓[/green] Command #{command_id} {status} favorites.")


@app.command()
def delete(
    command_id: int = typer.Argument(..., help="Command ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a command from history"""
    db = get_db()
    cmd = db.get_command(command_id)
    
    if not cmd:
        console.print(f"[red]Command #{command_id} not found.[/red]")
        raise typer.Exit(1)
    
    if not force:
        confirm = typer.confirm(f"Delete command: {cmd.command[:50]}...?")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            return
    
    db.delete_command(command_id)
    console.print(f"[green]✓[/green] Command #{command_id} deleted.")


@app.command()
def stats():
    """Show command history statistics"""
    db = get_db()
    analyzer = CommandAnalyzer(db)
    
    overview = analyzer.get_overview()
    productivity = analyzer.get_productivity_score()
    
    # Overview panel
    console.print(Panel(
        f"[bold]Total Commands:[/bold] {overview['total_commands']}\n"
        f"[bold]Productivity Score:[/bold] {productivity['score']}/100 ({productivity['level']})",
        title="📊 Statistics Overview",
        border_style="blue"
    ))
    
    # Category distribution
    if overview['categories']:
        cat_table = Table(title="Category Distribution")
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Count", style="green")
        cat_table.add_column("%", style="yellow")
        cat_table.add_column("Success Rate", style="blue")
        
        for cat, stats in sorted(overview['categories'].items(), 
                                key=lambda x: x[1].count, reverse=True)[:10]:
            cat_table.add_row(
                cat,
                str(stats.count),
                f"{stats.percentage}%",
                f"{stats.success_rate}%"
            )
        
        console.print(cat_table)
    
    # Insights
    if overview['insights']:
        console.print("\n[bold]💡 Insights:[/bold]")
        for insight in overview['insights']:
            console.print(f"  {insight}")


@app.command()
def analyze():
    """Run comprehensive analysis and show report"""
    db = get_db()
    analyzer = CommandAnalyzer(db)
    
    report = analyzer.export_report(format="text")
    console.print(report)


@app.command()
def tui():
    """Launch the interactive TUI interface"""
    from cmdmind.ui.app import CmdMindApp
    app = CmdMindApp()
    app.run()


@app.command()
def export(
    output: Path = typer.Option(Path("cmdmind_export.json"), "--output", "-o", help="Output file"),
    format: str = typer.Option("json", "--format", "-f", help="Export format (json, csv)"),
):
    """Export command history"""
    import json
    
    db = get_db()
    commands = db.get_recent_commands(limit=10000)
    
    if format == "json":
        data = {
            "version": __version__,
            "exported_at": datetime.now().isoformat(),
            "total_commands": len(commands),
            "commands": [cmd.to_dict() for cmd in commands]
        }
        
        with open(output, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        console.print(f"[green]✓[/green] Exported {len(commands)} commands to {output}")
    
    elif format == "csv":
        import csv
        
        with open(output, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "command", "category", "shell", "exit_code", 
                           "timestamp", "favorite", "use_count"])
            
            for cmd in commands:
                writer.writerow([
                    cmd.id, cmd.command, cmd.category, cmd.shell,
                    cmd.exit_code, cmd.timestamp, cmd.favorite, cmd.use_count
                ])
        
        console.print(f"[green]✓[/green] Exported {len(commands)} commands to {output}")


@app.command()
def clear(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Clear all command history"""
    db = get_db()
    
    if not force:
        confirm = typer.confirm("⚠️  This will delete ALL commands. Are you sure?")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            return
    
    count = db.clear_all()
    console.print(f"[green]✓[/green] Cleared {count} commands.")


# Import datetime for export command
from datetime import datetime


if __name__ == "__main__":
    app()
