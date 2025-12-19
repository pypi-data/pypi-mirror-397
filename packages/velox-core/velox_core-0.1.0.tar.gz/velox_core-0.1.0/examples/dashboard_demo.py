import asyncio
import sys
import os
sys.path.append(os.getcwd())

from velox.core.engine import Velox
from velox.providers.mock import MockProvider
from velox.layers.dashboard import DashboardLayer

async def main():
    motor = Velox()
    
    # Add Dashboard (Should be early in the chain to wrap everything)
    motor.add(DashboardLayer())
    
    motor.use(MockProvider(response_text="Data Received."))
    
    # Run
    await motor.prompt("Analyze sector 7G")

if __name__ == "__main__":
    asyncio.run(main())
