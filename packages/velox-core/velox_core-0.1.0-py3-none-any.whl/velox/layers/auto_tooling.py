import json
from typing import Callable, Awaitable, List, Dict, Any
from velox.core.context import EventContext
from velox.layers.base import Layer

class AutoToolingLayer(Layer):
    """
    Middleware that simplifies tool usage.
    It can inject tool definitions into the prompt and 
    parse tool-call responses.
    """
    def __init__(self, tools: List[Dict[str, Any]] = None, tool_map: Dict[str, Callable] = None):
        self.tools = tools or []
        self.tool_map = tool_map or {}

    async def process(
        self, 
        ctx: EventContext, 
        next_call: Callable[[EventContext], Awaitable[EventContext]]
    ) -> EventContext:
        # 1. Inject tool instructions if tools are provided
        if self.tools:
            ctx.metadata["available_tools"] = self.tools
            # We assume the provider handles 'tools' in metadata or similar
            # In a real scenario, we might append a system message
        
        # 2. Execute
        ctx = await next_call(ctx)
        
        # 3. Simple Mock Logic: Check if the response looks like a JSON tool call
        # (This is just for demonstration in this middleware context)
        if ctx.response_content and ctx.response_content.strip().startswith("{") and '"tool"' in ctx.response_content:
            try:
                tool_data = json.loads(ctx.response_content)
                tool_name = tool_data.get("tool")
                if tool_name in self.tool_map:
                    args = tool_data.get("args", {})
                    # In a real implementation, this would be async and handle the loop
                    # For now, we just tag it
                    ctx.metadata["tool_executed"] = tool_name
            except:
                pass

        return ctx
