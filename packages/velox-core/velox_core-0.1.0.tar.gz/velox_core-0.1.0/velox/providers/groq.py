import os
import httpx
from typing import Optional
from velox.providers.base import BaseProvider
from velox.core.context import EventContext, UsageMetrics

class GroqProvider(BaseProvider):
    """
    Groq LLM Integration using httpx (OpenAI-compatible).
    High-speed inference provider.
    """
    def __init__(self, api_key: str = None, model: str = "llama3-70b-8192"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API Key must be provided or set in GROQ_API_KEY env")
        
        self.default_model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate(self, ctx: EventContext) -> EventContext:
        model = ctx.model if ctx.model != "default" else self.default_model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in ctx.messages],
            "temperature": ctx.temperature,
            "max_tokens": ctx.max_tokens
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, headers=headers, json=data, timeout=60.0)
            response.raise_for_status()
            res_json = response.json()
            
        content = res_json["choices"][0]["message"]["content"]
        usage = res_json.get("usage", {})
        
        # Groq cost is currently very low/subsidized or free tier
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        
        # Approximate cost for Llama 3 70B on Groq
        cost = (prompt_tokens * 0.59 / 1_000_000) + (completion_tokens * 0.79 / 1_000_000)

        ctx.set_response(
            content=content,
            usage=UsageMetrics(
                total_tokens=usage.get("total_tokens", 0),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost_usd=cost
            )
        )
        
        return ctx
