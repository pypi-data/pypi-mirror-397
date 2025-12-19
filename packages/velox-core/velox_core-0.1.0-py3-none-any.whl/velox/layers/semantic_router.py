import re
from typing import Callable, Awaitable
from velox.core.context import EventContext
from velox.layers.base import Layer

class SemanticRouterLayer(Layer):
    """
    Middleware that routes simple prompts to a cheaper/faster model
    to optimize latency and cost.
    """
    def __init__(self, simple_model: str = "gpt-3.5-turbo", threshold_chars: int = 50):
        self.simple_model = simple_model
        self.threshold_chars = threshold_chars

    def _is_simple(self, text: str) -> bool:
        # Very basic check: short text, no complex punctuation, no "explain", etc.
        if len(text) > self.threshold_chars:
            return False
            
        complex_keywords = ["explain", "analyze", "complex", "detailed", "step-by-step"]
        if any(kw in text.lower() for kw in complex_keywords):
            return False
            
        return True

    async def process(
        self, 
        ctx: EventContext, 
        next_call: Callable[[EventContext], Awaitable[EventContext]]
    ) -> EventContext:
        # Get the latest user message
        last_user_msg = next((m for m in reversed(ctx.messages) if m.role == "user"), None)
        
        if last_user_msg and self._is_simple(last_user_msg.content):
            ctx.metadata["original_model"] = ctx.model
            ctx.model = self.simple_model
            ctx.metadata["routed_by"] = "SemanticRouter"
            
        return await next_call(ctx)
