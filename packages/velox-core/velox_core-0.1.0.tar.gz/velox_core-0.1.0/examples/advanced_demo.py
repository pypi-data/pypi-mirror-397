import asyncio
import sys
import os
sys.path.append(os.getcwd())

from velox.core.engine import Velox
from velox.providers.mock import MockProvider
from velox.layers.advanced_dashboard import AdvancedDashboardLayer
from velox.layers.resilience import RetryLayer

async def main():
    motor = Velox()
    
    # Use the Pro Dashboard
    motor.add(AdvancedDashboardLayer())
    motor.add(RetryLayer()) # Silent retry
    
    # Mock Provider for visual data
    long_response = """
    Here is the analysis of the sector.
    
    1. Alpha Node: Optimal
    2. Beta Node: Warning (Latency High)
    3. Gamma Node: Offline
    
    Recommendation: Re-route traffic through Alpha.
    """
    motor.use(MockProvider(response_text=long_response))
    
    await motor.prompt("System Status Report")

if __name__ == "__main__":
    asyncio.run(main())
