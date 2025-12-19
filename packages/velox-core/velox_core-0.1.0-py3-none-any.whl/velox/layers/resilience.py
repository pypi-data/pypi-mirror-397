import asyncio
from typing import Callable, Awaitable, Type
from velox.layers.base import Layer
from velox.core.context import EventContext

class RetryLayer(Layer):
    """
    Middleware that automatically retries the request if the provider fails.
    """
    def __init__(
        self, 
        max_retries: int = 3, 
        base_delay: float = 1.0, 
        exceptions: Type[Exception] = Exception
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.exceptions = exceptions

    async def process(self, ctx: EventContext, next_call: Callable) -> EventContext:
        attempt = 0
        while True:
            try:
                # Try to execute the rest of the pipeline
                return await next_call(ctx)
            except self.exceptions as e:
                attempt += 1
                if attempt > self.max_retries:
                    raise e
                
                # Exponential backoff
                delay = self.base_delay * (2 ** (attempt - 1))
                # Log usage inside context metadata for debugging
                ctx.metadata.setdefault("_logs", []).append(
                    f"Retry {attempt}/{self.max_retries} due to: {str(e)}"
                )
                await asyncio.sleep(delay)
