import asyncio
import sys
import os
sys.path.append(os.getcwd())

from velox.core.engine import Velox
from velox.providers.mock import MockProvider
from velox.layers.resilience import RetryLayer
from velox.layers.logging import LoggerLayer
from velox.layers.caching import CacheLayer
from rich.console import Console

console = Console()

async def main():
    motor = Velox()
    
    # 1. Setup the Pipeline (Order matters!)
    # Log -> Cache -> Retry -> Provider
    motor.add(LoggerLayer())
    motor.add(CacheLayer())
    motor.add(RetryLayer(max_retries=3, base_delay=0.1))
    
    # 2. Setup Provider
    # We tell it to fail twice, then succeed.
    motor.use(MockProvider(response_text="Success", fail_count=2))
    
    console.print("[bold white on blue] TEST 1: Retry Logic [/bold white on blue]")
    # Expect: 2 Retries logs, then Success
    await motor.prompt("Can you hear me?")
    
    console.print("\n[bold white on blue] TEST 2: Caching Logic [/bold white on blue]")
    # First call - costs money (simulated)
    console.print(">> Asking: 'What is 2+2?' (Miss)")
    await motor.prompt("What is 2+2?")
    
    # Second call - same prompt - should be instant and free
    console.print(">> Asking: 'What is 2+2?' (Hit)")
    await motor.prompt("What is 2+2?")

if __name__ == "__main__":
    asyncio.run(main())
