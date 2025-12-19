from typing import Dict
from velox.layers.base import Layer
from velox.core.context import EventContext, UsageMetrics

class CacheLayer(Layer):
    """
    Middleware that caches responses based on the prompt content.
    TODO: In the future, use Vector Similarity (Semantic Caching).
    """
    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._cache_hits = 0

    async def process(self, ctx: EventContext, next_call) -> EventContext:
        # Simple exact match key for now
        # Key = Model + Last User Message
        user_msg = ctx.messages[-1].content
        key = f"{ctx.model}:{user_msg}"

        if key in self._cache:
            ctx.set_response(
                content=self._cache[key],
                usage=UsageMetrics() # Zero cost for cache hit
            )
            ctx.metadata["cache_hit"] = True
            self._cache_hits += 1
            return ctx

        # No cache hit, proceed
        ctx = await next_call(ctx)

        # Cache the result
        if ctx.response_content:
            self._cache[key] = ctx.response_content
        
        ctx.metadata["cache_hit"] = False
        return ctx
