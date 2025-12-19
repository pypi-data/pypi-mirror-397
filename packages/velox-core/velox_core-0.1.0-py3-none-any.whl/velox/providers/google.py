import os
import asyncio
from typing import Optional
import google.generativeai as genai
from velox.providers.base import BaseProvider
from velox.core.context import EventContext, UsageMetrics

class GoogleGeminiProvider(BaseProvider):
    """
    Google Gemini LLM Integration.
    """
    def __init__(self, api_key: str = None, model: str = "gemini-1.5-pro-latest"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API Key must be provided or set in GOOGLE_API_KEY env")
        
        genai.configure(api_key=self.api_key)
        self.default_model = model

    async def generate(self, ctx: EventContext) -> EventContext:
        model_name = ctx.model if ctx.model != "default" else self.default_model
        
        model = genai.GenerativeModel(model_name)
        
        # Convert messages to Gemini format
        # Gemini usually takes history or just a prompt
        # For simplicity, we'll use start_chat for multi-turn if needed
        chat = model.start_chat(history=[
            {"role": "user" if m.role == "user" else "model", "parts": [m.content]}
            for m in ctx.messages[:-1]
        ])
        
        last_msg = ctx.messages[-1].content
        
        # run_in_executor if the SDK is blocking, but genai has async support usually
        # Actually genai.GenerativeModel.generate_content_async exists
        response = await model.generate_content_async(
            last_msg,
            generation_config=genai.types.GenerationConfig(
                temperature=ctx.temperature,
                max_output_tokens=ctx.max_tokens
            )
        )
        
        # Usage metrics
        # Gemini 1.5 usage is slightly different
        try:
            usage = response.usage_metadata
            prompt_tokens = usage.prompt_token_count
            completion_tokens = usage.candidates_token_count
            total_tokens = usage.total_token_count
        except:
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0

        # Cost estimation (Gemini 1.5 Pro is free within limits or cheap)
        cost = (prompt_tokens * 3.5 / 1_000_000) + (completion_tokens * 10.5 / 1_000_000)

        ctx.set_response(
            content=response.text,
            usage=UsageMetrics(
                total_tokens=total_tokens,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost_usd=cost
            )
        )
        
        return ctx
