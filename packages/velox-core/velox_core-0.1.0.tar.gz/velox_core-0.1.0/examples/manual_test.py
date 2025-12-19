import asyncio
import sys
import os

# Add the project root to path so we can import velox
sys.path.append(os.getcwd())

from velox.core.engine import Velox
from velox.providers.mock import MockProvider
from velox.layers.base import Layer
from velox.core.context import EventContext

# Define a simple Test Layer
class PrintLayer(Layer):
    async def process(self, ctx: EventContext, next_call):
        print(f"[Layer] >> Incoming: {ctx.messages[-1].content}")
        ctx = await next_call(ctx)
        print(f"[Layer] << Outgoing: {ctx.response_content}")
        return ctx

async def main():
    print("Initializing Velox Engine...")
    motor = Velox()
    
    # Add Middleware
    motor.add(PrintLayer())
    
    # Set Provider
    motor.use(MockProvider(response_text="Velox is online"))
    
    print("Running Prompt...")
    response = await motor.prompt("Test Fire")
    
    print(f"\nFinal Result: {response}")

if __name__ == "__main__":
    asyncio.run(main())
