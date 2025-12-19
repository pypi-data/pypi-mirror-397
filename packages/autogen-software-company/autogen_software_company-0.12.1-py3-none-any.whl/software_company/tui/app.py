from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, RichLog
from textual.containers import Container, Horizontal, Vertical
from textual.worker import Worker
from datetime import datetime
import asyncio

from .widgets import TimelineWidget, StatsWidget
from .adapter import TuiUIAdapter
from ..workflow import SoftwareCompanyWorkflow

class SoftwareCompanyApp(App):
    CSS = """
    TimelineWidget {
        width: 30%;
        height: 100%;
        dock: left;
    }

    StatsWidget {
        height: 5;
        dock: bottom;
    }

    RichLog {
        border: solid green;
    }
    """

    def __init__(self, workflow_factory, **kwargs):
        super().__init__(**kwargs)
        self._workflow_factory = workflow_factory
        self.workflow = None
        self.start_time = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            TimelineWidget(steps=[]), # Initial empty, will update
            RichLog(highlight=True, markup=True, id="main_log"),
        )
        yield StatsWidget()
        yield Footer()

    async def on_mount(self):
        # We need to instantiate the workflow here because we need to pass the adapter
        # which needs 'self' (the app).

        adapter = TuiUIAdapter(self)

        # The factory is a partial or callable that takes 'ui'
        self.workflow = self._workflow_factory(ui=adapter)

        # Initialize widgets
        timeline = self.query_one(TimelineWidget)
        timeline.steps = self.workflow.steps
        timeline.current_step_index = self.workflow.state_manager.get_current_step_index()

        self.start_time = datetime.now()
        self.set_interval(1, self.update_timer)

        # Run the workflow in a worker
        self.run_worker(self.run_workflow_task, exclusive=True)

    async def run_workflow_task(self):
        try:
            # We assume 'run' is an async method on the workflow
            # We need to know arguments for run().
            # Ideally the factory or main.py set up the prompt/args.
            # But workflow.run() takes optional args.
            # We might need to pass them in via factory or similar.
            # Let's assume the workflow object is fully configured.

            # The run method signature is async def run(self, user_request: str = "", single_step: bool = False):
            # We might need to pass user_request if it's a new task.
            # However, main.py logic handles initializing context with user_request BEFORE calling run if it was passed.
            # Let's check main.py again...
            # Yes, main.py calls `await workflow.run(prompt if prompt else "", single_step=args.step)`
            # So we need to be able to pass these.

            # We will rely on the factory to have set up the workflow instance correctly,
            # or simply call run with empty string if context is already set.
            # But wait, main.py logic is:
            # `workflow = SoftwareCompanyWorkflow(...)`
            # `await workflow.run(...)`

            # So `self.workflow` is the instance.

            # Hack: we will check if "user_request" is in context. If not, we might need it.
            # But the TuiAdapter injection happens at init.

            await self.workflow.run()

        except Exception as e:
            self.log(f"[bold red]Workflow Crashed: {e}[/bold red]")

    def on_step_start(self, step_number: int, step_name: str):
        timeline = self.query_one(TimelineWidget)
        # step_number is 1-based index
        timeline.current_step_index = step_number - 1
        self.log(f"[bold blue]Step {step_number}: {step_name}[/bold blue]")

    def log(self, message: str):
        log_widget = self.query_one("#main_log", RichLog)
        log_widget.write(message)

    def stream_log(self, text: str):
        log_widget = self.query_one("#main_log", RichLog)
        # Using write with end="" if possible, but RichLog.write adds newline by default?
        # RichLog writes lines. Streaming might be tricky if we want char-by-char.
        # But 'text' from callbacks is usually chunks.
        log_widget.write(text)

    def update_status(self, message: str):
        stats = self.query_one(StatsWidget)
        stats.status_message = message

    def update_timer(self):
        if self.start_time:
            delta = datetime.now() - self.start_time
            stats = self.query_one(StatsWidget)
            stats.execution_time = str(delta).split('.')[0]
