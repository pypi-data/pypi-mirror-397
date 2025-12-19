from velox.layers.base import Layer
from velox.core.context import EventContext
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console
import asyncio

class DashboardLayer(Layer):
    """
    Middleware that provides a "Pro" TUI experience.
    Shows a spinner during generation and a stats table after.
    """
    def __init__(self):
        self.console = Console()

    async def process(self, ctx: EventContext, next_call) -> EventContext:
        # Create a layout or simple renderable
        spinner = Spinner("dots", text=f"Velox Engine Running... [Model: {ctx.model}]")
        
        # Use Live display to show spinner
        with Live(spinner, refresh_per_second=10) as live:
            # Execute pipeline
            ctx = await next_call(ctx)
            
            # Update to done
            live.update(Spinner("dots", text="Done!", style="green"))
            await asyncio.sleep(0.5) # Brief pause to see green

        # Print Final Stats Table
        table = Table(title="Velox Telemetry", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="dim")
        table.add_column("Value")
        
        table.add_row("Latency", f"{ctx.metrics.latency_ms:.2f} ms")
        table.add_row("Total Tokens", str(ctx.metrics.total_tokens))
        table.add_row("Cost", f"${ctx.metrics.cost_usd:.6f}")
        table.add_row("Provider", ctx.model)
        
        self.console.print(table)
        return ctx
