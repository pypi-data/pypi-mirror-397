from __future__ import annotations
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from velox.core.context import EventContext, Message
from velox.core.pipeline import Pipeline

if TYPE_CHECKING:
    from velox.layers.base import Layer
    from velox.providers.base import BaseProvider

class Velox:
    """
    The High-Performance Motor.
    """
    def __init__(self):
        self._pipeline = Pipeline()

    def add(self, layer: Layer):
        """Add a middleware layer to the pipeline."""
        self._pipeline.add_layer(layer)
        return self

    def use(self, provider: BaseProvider):
        """Set the LLM provider."""
        self._pipeline.set_provider(provider)
        return self

    async def run(
        self, 
        messages: List[Message], 
        model: str = "default",
        **kwargs
    ) -> EventContext:
        """
        Run the motor.
        """
        ctx = EventContext(
            messages=messages,
            model=model,
            metadata=kwargs.get("metadata", {}),
            **kwargs
        )
        return await self._pipeline.run(ctx)

    async def prompt(self, text: str, **kwargs) -> str:
        """
        Legacy/Simple helper for single-turn prompts.
        Returns just the content string.
        """
        msg = Message(role="user", content=text)
        ctx = await self.run(messages=[msg], **kwargs)
        return ctx.response_content
