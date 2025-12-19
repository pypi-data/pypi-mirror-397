from textual.widgets import Static, RichLog
from textual.app import ComposeResult
from textual.reactive import reactive
from rich.panel import Panel
from rich.table import Table

class TimelineWidget(Static):
    """Displays the workflow timeline/steps."""

    current_step_index = reactive(0)
    steps = reactive([])

    def __init__(self, steps: list, **kwargs):
        super().__init__(**kwargs)
        self.steps = steps

    def on_mount(self):
        self.update_timeline()

    def watch_current_step_index(self, old_val, new_val):
        self.update_timeline()

    def update_timeline(self):
        grid = Table.grid(expand=True)
        grid.add_column(style="dim")
        grid.add_column()
        grid.add_column(justify="right")

        for i, step in enumerate(self.steps):
            idx = i + 1
            name = step.name

            if i < self.current_step_index:
                status = "[green]✓[/green]"
                style = "dim"
            elif i == self.current_step_index:
                status = "[blue]▶[/blue]"
                style = "bold blue"
            else:
                status = " "
                style = "dim"

            grid.add_row(f"{idx}.", f"[{style}]{name}[/{style}]", status)

        self.update(Panel(grid, title="Timeline", border_style="blue"))


class StatsWidget(Static):
    """Displays execution statistics."""

    execution_time = reactive("00:00")
    status_message = reactive("Ready")

    def render(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right", ratio=1)

        grid.add_row(f"Status: {self.status_message}", f"Time: {self.execution_time}")
        return Panel(grid, title="Stats", border_style="green")
