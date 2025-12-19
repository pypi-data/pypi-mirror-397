from typing import Callable, Awaitable, Dict
from velox.core.context import EventContext
from velox.layers.base import Layer

class CostOptimizerLayer(Layer):
    """
    Middleware that tracks and limits AI spend.
    It can enforce a per-session or per-request budget.
    """
    # Simple in-memory session tracking
    _session_costs: Dict[str, float] = {}

    def __init__(self, max_cost_usd: float = 0.5, per_request: bool = False):
        self.max_cost_usd = max_cost_usd
        self.per_request = per_request

    async def process(
        self, 
        ctx: EventContext, 
        next_call: Callable[[EventContext], Awaitable[EventContext]]
    ) -> EventContext:
        session_id = ctx.session_id
        
        # 1. Check current Spend
        current_spend = self._session_costs.get(session_id, 0.0)
        
        if not self.per_request and current_spend >= self.max_cost_usd:
            raise Exception(f"Budget exceeded for session {session_id}. Limit: ${self.max_cost_usd}")

        # 2. Execute the chain
        ctx = await next_call(ctx)
        
        # 3. Update Spend after response
        new_cost = ctx.metrics.cost_usd
        if self.per_request:
            if new_cost >= self.max_cost_usd:
                 # This happens after the fact, but good for logging/metrics
                 pass
        else:
            self._session_costs[session_id] = current_spend + new_cost
            
        return ctx
