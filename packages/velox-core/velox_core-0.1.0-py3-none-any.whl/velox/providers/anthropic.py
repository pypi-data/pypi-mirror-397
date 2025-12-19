import os
import httpx
from typing import Optional
from velox.providers.base import BaseProvider
from velox.core.context import EventContext, UsageMetrics

class AnthropicProvider(BaseProvider):
    """
    Anthropic (Claude) LLM Integration using httpx.
    """
    def __init__(self, api_key: str = None, model: str = "claude-3-5-sonnet-20240620"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API Key must be provided or set in ANTHROPIC_API_KEY env")
        
        self.default_model = model
        self.base_url = "https://api.anthropic.com/v1/messages"

    async def generate(self, ctx: EventContext) -> EventContext:
        model = ctx.model if ctx.model != "default" else self.default_model
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in ctx.messages],
            "max_tokens": ctx.max_tokens or 1024,
            "temperature": ctx.temperature
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, headers=headers, json=data, timeout=60.0)
            response.raise_for_status()
            res_json = response.json()
            
        content = res_json["content"][0]["text"]
        usage = res_json.get("usage", {})
        
        # Approximate cost for Claude 3.5 Sonnet
        prompt_tokens = usage.get("input_tokens", 0)
        completion_tokens = usage.get("output_tokens", 0)
        cost = (prompt_tokens * 3.0 / 1_000_000) + (completion_tokens * 15.0 / 1_000_000)

        ctx.set_response(
            content=content,
            usage=UsageMetrics(
                total_tokens=prompt_tokens + completion_tokens,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost_usd=cost
            )
        )
        
        return ctx
