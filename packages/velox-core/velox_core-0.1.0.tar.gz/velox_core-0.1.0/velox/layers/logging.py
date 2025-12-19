from velox.layers.base import Layer
from velox.core.context import EventContext
from rich.console import Console
from rich.panel import Panel

console = Console()

class LoggerLayer(Layer):
    """
    Middleware that prints pretty logs of the request execution using Rich.
    """
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    async def process(self, ctx: EventContext, next_call) -> EventContext:
        # 1. Log Request
        console.print(Panel(
            f"[bold blue]Model:[/bold blue] {ctx.model}\n[bold yellow]Input:[/bold yellow] {ctx.messages[-1].content}",
            title="[Incoming Request]",
            border_style="blue"
        ))

        # 2. Execute
        try:
            ctx = await next_call(ctx)
        except Exception as e:
            console.print(f"[bold red]Pipeline Error:[/bold red] {e}")
            raise e

        # 3. Log Response
        stats = f"Latency: {ctx.metrics.latency_ms:.1f}ms | Cost: ${ctx.metrics.cost_usd:.6f}"
        console.print(Panel(
            f"[bold green]Response:[/bold green] {ctx.response_content}\n\n[dim]{stats}[/dim]",
            title="[Pipeline Complete]",
            border_style="green"
        ))
        
        return ctx
