from velox.providers.base import BaseProvider
from velox.core.context import EventContext, UsageMetrics
from openai import AsyncOpenAI
import os

class OpenAIProvider(BaseProvider):
    """
    Production-grade OpenAI integration.
    """
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        # Use env var if not provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API Key must be provided or set in OPENAI_API_KEY env")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.default_model = model

    async def generate(self, ctx: EventContext) -> EventContext:
        # Determine model
        model = ctx.model if ctx.model != "default" else self.default_model
        
        # Call OpenAI
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in ctx.messages],
            temperature=ctx.temperature,
            max_tokens=ctx.max_tokens
        )
        
        # Parse Response
        choice = response.choices[0]
        usage = response.usage
        
        # Calculate approximate cost (Rough estimates for Gpt-4o for now)
        # TODO: Implement a proper CostMap
        cost = 0.0
        if usage:
            # $5.00 / 1M input, $15.00 / 1M output
            cost = (usage.prompt_tokens * 5.0 / 1_000_000) + \
                   (usage.completion_tokens * 15.0 / 1_000_000)

        ctx.set_response(
            content=choice.message.content,
            usage=UsageMetrics(
                total_tokens=usage.total_tokens if usage else 0,
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0,
                cost_usd=cost
            )
        )
        
        return ctx
