from abc import ABC, abstractmethod
from velox.core.context import EventContext

class BaseProvider(ABC):
    """
    Interface for LLM Providers (OpenAI, Anthropic, Mock).
    The Provider is always the *last* link in the pipeline.
    """
    
    @abstractmethod
    async def generate(self, ctx: EventContext) -> EventContext:
        """
        Send the request to the actual LLM API.
        Must populate ctx.response_content and ctx.metrics.
        """
        pass
