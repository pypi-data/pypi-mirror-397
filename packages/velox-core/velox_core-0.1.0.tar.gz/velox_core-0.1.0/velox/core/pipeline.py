from __future__ import annotations
from typing import List, Callable, Awaitable, TYPE_CHECKING
from velox.core.context import EventContext

if TYPE_CHECKING:
    from velox.layers.base import Layer
    from velox.providers.base import BaseProvider

class Pipeline:
    """
    The heart of the Motor.
    Manages the chain of middleware layers and the final provider execution.
    """
    def __init__(self):
        self._layers: List[Layer] = []
        self._provider: BaseProvider = None

    def add_layer(self, layer: Layer):
        self._layers.append(layer)

    def set_provider(self, provider: BaseProvider):
        self._provider = provider

    async def run(self, ctx: EventContext) -> EventContext:
        """
        Execute the pipeline.
        Basic recursive/chain implementation.
        """
        if not self._provider:
            raise ValueError("No provider set for the pipeline!")

        # 1. Define the final step (calling the provider)
        async def call_provider(c: EventContext) -> EventContext:
            return await self._provider.generate(c)

        # 2. Build the chain backwards
        # The last middleware calls 'call_provider'
        # The second-to-last calls the last, etc.
        next_call = call_provider
        
        for layer in reversed(self._layers):
            # Capture the current 'next_call' in a closure
            def make_bound_next(current_layer, current_next):
                async def bound_next(c: EventContext) -> EventContext:
                    return await current_layer.process(c, current_next)
                return bound_next
            
            next_call = make_bound_next(layer, next_call)

        # 3. Execute the first step of the chain
        return await next_call(ctx)
