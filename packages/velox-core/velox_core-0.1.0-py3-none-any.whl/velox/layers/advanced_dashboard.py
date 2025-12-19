from velox.layers.base import Layer
from velox.core.context import EventContext
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from datetime import datetime
import asyncio

class AdvancedDashboardLayer(Layer):
    """
    The Pro 'Dark Mode' Dashboard.
    Uses a full-screen layout to visualize the motor's state.
    """
    def __init__(self):
        self.console = Console()
        self.history = []

    def make_layout(self) -> Layout:
        """Define the grid."""
        layout = Layout(name="root")
        
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="side", ratio=1),
            Layout(name="body", ratio=3)
        )
        return layout

    def render_view(self, ctx: EventContext, status: str) -> Layout:
        layout = self.make_layout()
        
        # Header
        layout["header"].update(
            Panel(f"[bold cyan]VELOX CORE ENGINE[/bold cyan] | Status: {status}", style="on black")
        )
        
        # Sidebar (Metrics)
        stats = Table.grid(padding=1)
        stats.add_column(style="green", justify="right")
        stats.add_column(style="magenta")
        stats.add_row("Model", ctx.model)
        stats.add_row("Tokens", str(ctx.metrics.total_tokens))
        stats.add_row("Cost", f"${ctx.metrics.cost_usd:.6f}")
        stats.add_row("Latency", f"{ctx.metrics.latency_ms:.1f}ms")
        
        layout["side"].update(
            Panel(stats, title="[Metrics]", border_style="green")
        )

        # Body (The Response)
        content = ctx.response_content or "[dim]Waiting for motor content...[/dim]"
        layout["body"].update(
            Panel(content, title=f"[Response: {ctx.model}]", border_style="blue")
        )

        # Footer
        layout["footer"].update(
            Panel(f"[dim]Velox Session: {ctx.session_id} | {datetime.now().strftime('%H:%M:%S')}[/dim]", style="black")
        )
        
        return layout

    async def process(self, ctx: EventContext, next_call) -> EventContext:
        layout = self.make_layout()
        
        with Live(self.render_view(ctx, "IGNITION"), refresh_per_second=10, screen=True) as live:
            live.update(self.render_view(ctx, "PROCESSING"))
            
            # Execute
            ctx = await next_call(ctx)
            
            live.update(self.render_view(ctx, "COMPLETE"))
            await asyncio.sleep(2.0) # Hold screen for a moment
            
        return ctx
