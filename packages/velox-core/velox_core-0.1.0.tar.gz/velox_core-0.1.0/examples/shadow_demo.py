import asyncio
import sys
import os
sys.path.append(os.getcwd())

from velox.core.engine import Velox
from velox.providers.mock import MockProvider
from velox.layers.shadow import ShadowLayer
from velox.layers.logging import LoggerLayer

async def main():
    motor = Velox()
    
    # 1. Setup Shadow Mode
    # "Shadow" is a cheaper model we want to test.
    shadow_provider = MockProvider(response_text="I am the cheaper shadow model")
    
    motor.add(ShadowLayer(shadow_provider, name="Llama-3-8b"))
    motor.add(LoggerLayer()) # Logger will show the MAIN response
    
    # 2. Setup Main Provider
    # "Main" is GPT-4
    motor.use(MockProvider(response_text="I am the expensive GPT-4"))
    
    print("Sending Request... (Shadow should run in background)")
    await motor.prompt("Hello?")
    
    # Wait a bit to let the background shadow finish printing
    await asyncio.sleep(0.2)

if __name__ == "__main__":
    asyncio.run(main())
