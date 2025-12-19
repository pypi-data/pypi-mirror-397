from velox.providers.base import BaseProvider
from velox.core.context import EventContext, UsageMetrics
import asyncio

class MockProvider(BaseProvider):
    def __init__(self, response_text: str = "Mock Response", fail_count: int = 0):
        self.response_text = response_text
        self.fail_count = fail_count
        self.current_fails = 0

    async def generate(self, ctx: EventContext) -> EventContext:
        await asyncio.sleep(0.1)
        
        # Simulate Error
        if self.current_fails < self.fail_count:
            self.current_fails += 1
            raise Exception("Simulated Provider Error")
        
        ctx.set_response(
            content=f"{self.response_text} (Echo: {ctx.messages[-1].content})",
            usage=UsageMetrics(
                total_tokens=10,
                prompt_tokens=5,
                completion_tokens=5,
                cost_usd=0.0001
            )
        )
        return ctx
