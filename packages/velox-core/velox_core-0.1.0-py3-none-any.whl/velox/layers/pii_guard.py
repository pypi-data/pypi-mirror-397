import re
from typing import Callable, Awaitable, List
from velox.core.context import EventContext
from velox.layers.base import Layer

class PIIGuardLayer(Layer):
    """
    Middleware that redacts PII (Personally Identifiable Information) 
    from outgoing messages before they reach the provider.
    """
    def __init__(self, patterns: List[str] = None):
        # Default patterns for emails and phone numbers
        self.patterns = patterns or [
            r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',  # Email
            r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Phone
        ]
        self.regex = [re.compile(p) for p in self.patterns]

    def _redact(self, text: str) -> str:
        for r in self.regex:
            text = r.sub("[REDACTED]", text)
        return text

    async def process(
        self, 
        ctx: EventContext, 
        next_call: Callable[[EventContext], Awaitable[EventContext]]
    ) -> EventContext:
        # Redact messages
        for msg in ctx.messages:
            msg.content = self._redact(msg.content)
        
        # Pass to next layer
        return await next_call(ctx)
