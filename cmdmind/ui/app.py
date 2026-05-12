"""
CmdMind TUI Application
Interactive terminal user interface built with Textual
"""

from datetime import datetime
from typing import Optional, List
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header, Footer, Static, Input, Button, Label,
    DataTable, TabbedContent, TabPane, ListItem, ListView
)
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import Screen
from textual import events
from rich.text import Text
from rich.style import Style

from cmdmind.core.database import CommandDatabase, Command
from cmdmind.core.classifier import CommandClassifier
from cmdmind.core.searcher import CommandSearcher, SearchResult
from cmdmind.core.analyzer import CommandAnalyzer


class CommandList(DataTable):
    """Widget for displaying command list"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.commands: List[Command] = []
    
    def update_commands(self, commands: List[Command]) -> None:
        """Update the command list"""
        self.clear(columns=True)
        self.add_column("ID", width=5)
        self.add_column("Command", width=50)
        self.add_column("Category", width=10)
        self.add_column("Time", width=12)
        self.add_column("★", width=2)
        
        self.commands = commands
        
        for cmd in commands:
            time_str = cmd.timestamp.strftime("%m/%d %H:%M") if cmd.timestamp else ""
            fav = "★" if cmd.favorite else ""
            self.add_row(
                str(cmd.id),
                cmd.command[:50] + ("..." if len(cmd.command) > 50 else ""),
                cmd.category,
                time_str,
                fav
            )


class SearchInput(Input):
    """Search input widget"""
    
    def __init__(self, **kwargs):
        super().__init__(
            placeholder="🔍 Search commands... (Enter to search, Esc to clear)",
            **kwargs
        )


class StatsPanel(Static):
    """Statistics panel widget"""
    
    def update_stats(self, stats: dict) -> None:
        """Update statistics display"""
        lines = [
            "[bold blue]📊 Statistics[/bold blue]",
            "",
            f"Total Commands: [green]{stats.get('total_commands', 0)}[/green]",
            "",
            "[bold]Top Categories:[/bold]",
        ]
        
        for cat, count in list(stats.get('by_category', {}).items())[:5]:
            lines.append(f"  • {cat}: {count}")
        
        self.update("\n".join(lines))


class MainScreen(Screen):
    """Main application screen"""
    
    CSS = """
    MainScreen {
        layout: vertical;
    }
    
    .search-container {
        height: 3;
        padding: 1;
        background: $surface;
    }
    
    .main-container {
        layout: horizontal;
        height: 1fr;
    }
    
    .command-list {
        width: 2fr;
    }
    
    .detail-panel {
        width: 1fr;
        padding: 1;
        background: $surface;
        border-left: solid $primary;
    }
    
    .stats-panel {
        width: 1fr;
        padding: 1;
        background: $surface;
        border-left: solid $primary;
    }
    
    SearchInput {
        width: 100%;
    }
    
    CommandList {
        height: 1fr;
    }
    
    .detail-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .detail-command {
        background: $surface-darken-1;
        padding: 1;
        margin-bottom: 1;
    }
    
    .action-buttons {
        height: auto;
        layout: horizontal;
        margin-top: 1;
    }
    
    Button {
        margin-right: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("s", "focus_search", "Search"),
        Binding("r", "refresh", "Refresh"),
        Binding("f", "toggle_favorite", "Favorite"),
        Binding("d", "delete_command", "Delete"),
        Binding("enter", "copy_command", "Copy"),
        Binding("tab", "next_tab", "Next Tab"),
        Binding("shift+tab", "prev_tab", "Prev Tab"),
    ]
    
    current_commands: reactive[List[Command]] = reactive(list)
    selected_command: reactive[Optional[Command]] = reactive(None)
    
    def __init__(self, db: CommandDatabase):
        super().__init__()
        self.db = db
        self.classifier = CommandClassifier()
        self.searcher = CommandSearcher(db)
        self.analyzer = CommandAnalyzer(db)
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="search-container"):
            yield SearchInput(id="search-input")
        with Container(classes="main-container"):
            with Container(classes="command-list"):
                yield CommandList(id="command-list")
            with Container(classes="detail-panel"):
                yield Static(id="detail-content", classes="detail-title")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize on mount"""
        self.load_commands()
        self.query_one("#search-input").focus()
    
    def load_commands(self) -> None:
        """Load commands from database"""
        commands = self.db.get_recent_commands(limit=100)
        self.current_commands = commands
        self.update_command_list(commands)
    
    def update_command_list(self, commands: List[Command]) -> None:
        """Update the command list widget"""
        command_list = self.query_one("#command-list", CommandList)
        command_list.update_commands(commands)
    
    def update_detail_panel(self, cmd: Optional[Command]) -> None:
        """Update the detail panel"""
        detail = self.query_one("#detail-content", Static)
        
        if cmd is None:
            detail.update("[dim]Select a command to view details[/dim]")
            return
        
        lines = [
            f"[bold blue]Command #{cmd.id}[/bold blue]",
            "",
            f"[cyan]{cmd.command}[/cyan]",
            "",
            f"[bold]Category:[/bold] {cmd.category}",
            f"[bold]Shell:[/bold] {cmd.shell}",
            f"[bold]Exit Code:[/bold] {cmd.exit_code}",
            f"[bold]Time:[/bold] {cmd.timestamp.strftime('%Y-%m-%d %H:%M:%S') if cmd.timestamp else 'N/A'}",
            f"[bold]Use Count:[/bold] {cmd.use_count}",
            f"[bold]Favorite:[/bold] {'★ Yes' if cmd.favorite else 'No'}",
            "",
            f"[bold]Tags:[/bold] {', '.join(cmd.tags) if cmd.tags else 'None'}",
            "",
            f"[bold]Description:[/bold]",
            f"  {cmd.description or 'N/A'}",
        ]
        
        detail.update("\n".join(lines))
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection"""
        command_list = self.query_one("#command-list", CommandList)
        row_index = event.row_index
        
        if 0 <= row_index < len(command_list.commands):
            self.selected_command = command_list.commands[row_index]
            self.update_detail_panel(self.selected_command)
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search input"""
        query = event.value.strip()
        
        if not query:
            self.load_commands()
            return
        
        results = self.searcher.search(query, limit=50)
        commands = [r.command for r in results]
        self.current_commands = commands
        self.update_command_list(commands)
    
    def action_focus_search(self) -> None:
        """Focus the search input"""
        self.query_one("#search-input").focus()
    
    def action_refresh(self) -> None:
        """Refresh command list"""
        self.load_commands()
    
    def action_toggle_favorite(self) -> None:
        """Toggle favorite status"""
        if self.selected_command:
            self.selected_command.favorite = not self.selected_command.favorite
            self.db.update_command(self.selected_command)
            self.update_command_list(self.current_commands)
            self.update_detail_panel(self.selected_command)
    
    def action_delete_command(self) -> None:
        """Delete selected command"""
        if self.selected_command:
            self.db.delete_command(self.selected_command.id)
            self.selected_command = None
            self.load_commands()
    
    def action_copy_command(self) -> None:
        """Copy selected command to clipboard"""
        if self.selected_command:
            try:
                import pyperclip
                pyperclip.copy(self.selected_command.command)
                self.notify("Command copied to clipboard!", title="Copied")
            except Exception:
                self.notify("Could not copy to clipboard", title="Error", severity="error")


class CmdMindApp(App):
    """Main CmdMind TUI Application"""
    
    CSS = """
    CmdMindApp {
        background: $surface;
    }
    """
    
    TITLE = "CmdMind - AI-Powered Terminal Command Intelligence"
    SUB_TITLE = "Smart command history management"
    
    SCREENS = {
        "main": MainScreen,
    }
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
    ]
    
    def __init__(self):
        super().__init__()
        self.db = CommandDatabase()
    
    def on_mount(self) -> None:
        """Mount the main screen"""
        self.push_screen(MainScreen(self.db))


if __name__ == "__main__":
    app = CmdMindApp()
    app.run()
