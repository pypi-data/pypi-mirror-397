from textual.app import App
from typing import List, Optional
from ..ui import UserInterface

class TuiUIAdapter(UserInterface):
    """
    Adapter that bridges the Workflow engine (UserInterface protocol)
    to the Textual App instance.
    """
    def __init__(self, app: App):
        self.app = app

    def print_step_header(self, step_number: int, step_name: str, work_dir: str = None):
        self.app.call_from_thread(self.app.on_step_start, step_number, step_name)

    def print_assignment(self, role: str, tool: str, model: str):
        self.app.call_from_thread(self.app.log, f"[bold]Assignment:[/bold] Role={role}, Tool={tool}, Model={model}")

    def print_timeout(self, timeout_val: int):
        self.app.call_from_thread(self.app.log, f"[yellow]Timeout set to {timeout_val}s[/yellow]")

    def print_input_loading(self, input_key: str, path: str):
        self.app.call_from_thread(self.app.log, f"Loading input {input_key} from {path}")

    def print_tool_start(self, step_name: str, tool_name: str):
        self.app.call_from_thread(self.app.log, f"[green]Starting {step_name} via {tool_name}...[/green]")

    def start_spinner(self, message: str):
        # Textual handles loading via widgets or headers mostly,
        # but we can update status
        self.app.call_from_thread(self.app.update_status, message)

    def stop_spinner(self):
        self.app.call_from_thread(self.app.update_status, "Ready")

    def print_output(self, step_name: str, output: dict):
        self.app.call_from_thread(self.app.log, f"[bold success]--- Output from {step_name} ---[/bold success]")
        import json
        self.app.call_from_thread(self.app.log, json.dumps(output, indent=2))

    def print_error(self, message: str):
        self.app.call_from_thread(self.app.log, f"[bold red]ERROR: {message}[/bold red]")

    def print_warning(self, message: str):
        self.app.call_from_thread(self.app.log, f"[bold yellow]WARNING: {message}[/bold yellow]")

    def print_info(self, message: str):
        self.app.call_from_thread(self.app.log, f"[dim]{message}[/dim]")

    def print_success(self, message: str):
        self.app.call_from_thread(self.app.log, f"[bold green]{message}[/bold green]")

    def print_stream_line(self, line: str, source: str = "stdout"):
        # For streaming, we append to the log widget
        self.app.call_from_thread(self.app.stream_log, line)

    def input(self, prompt: str) -> str:
        # Input in TUI is tricky if the workflow is in a thread.
        # We'd need to pause execution and wait for UI event.
        # For now, we'll raise NotImplementedError or handle it if we have time to implement a modal.
        # Given the complexity, we might skip full interactive input support in the first pass
        # or implement a simple workaround.
        # TODO: Implement interactive input via Worker.wait() or similar
        return ""

    def print_user_intervention(self, step_name: str, files: list):
        self.app.call_from_thread(self.app.log, f"[bold yellow]USER INTERVENTION REQUIRED for {step_name}[/bold yellow]")
        for k, p in files:
            self.app.call_from_thread(self.app.log, f" - {k}: {p}")
