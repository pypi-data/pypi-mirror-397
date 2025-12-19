from abc import ABC, abstractmethod
from typing import Callable, Awaitable
from velox.core.context import EventContext

class Layer(ABC):
    """
    Base class for all Velox Middleware.
    Layers can intercept requests before they reach the provider,
    and inspect responses after they return.
    """
    
    @abstractmethod
    async def process(
        self, 
        ctx: EventContext, 
        next_call: Callable[[EventContext], Awaitable[EventContext]]
    ) -> EventContext:
        """
        Process the request.
        
        Args:
            ctx: The current EventContext.
            next_call: The next layer in the pipeline (or the provider).
            
        Returns:
            The modified (or finalized) EventContext.
        """
        pass
