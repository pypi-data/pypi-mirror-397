import asyncio
from typing import Callable
from velox.layers.base import Layer
from velox.providers.base import BaseProvider
from velox.core.context import EventContext
from rich.console import Console

console = Console()

class ShadowLayer(Layer):
    """
    Middleware that runs a 'Shadow Model' in parallel.
    The shadow result is computed but NOT returned to the user.
    Useful for testing new models or comparing cost/quality.
    """
    def __init__(self, shadow_provider: BaseProvider, name: str = "Shadow"):
        self.shadow_provider = shadow_provider
        self.name = name

    async def process(self, ctx: EventContext, next_call: Callable) -> EventContext:
        # 1. Clone context for the shadow (deep copy needed ideally, but shallow ok for now)
        # We need a fresh context so we don't mess up the main one's metrics
        shadow_ctx = EventContext(
            messages=ctx.messages,
            model=f"{ctx.model}-shadow",
            metadata=ctx.metadata.copy()
        )

        # 2. Define the background task
        async def run_shadow():
            try:
                result = await self.shadow_provider.generate(shadow_ctx)
                # Log shadow result
                console.print(f"[dim i]>> Shadow ({self.name}) finished: {result.response_content} (Lat: {result.metrics.latency_ms:.1f}ms)[/dim i]")
            except Exception as e:
                console.print(f"[dim red]>> Shadow ({self.name}) failed: {e}[/dim red]")

        # 3. Fire and Forget
        asyncio.create_task(run_shadow())

        # 4. Continue main pipeline
        return await next_call(ctx)
