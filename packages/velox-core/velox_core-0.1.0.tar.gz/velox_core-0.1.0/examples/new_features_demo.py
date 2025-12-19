import asyncio
import sys
import os
sys.path.insert(0, os.getcwd())

from velox.core.engine import Velox
from velox.providers.mock import MockProvider
from velox.layers import (
    PIIGuardLayer, 
    CostOptimizerLayer, 
    SemanticRouterLayer, 
    LoggerLayer
)

async def main():
    print("--- Velox-Core Advanced Features Demo ---\n")
    
    motor = Velox()
    
    # 1. Add PII Guard (Redacts emails/phones)
    motor.add(PIIGuardLayer())
    
    # 2. Add Semantic Router (Switches model for simple prompts)
    motor.add(SemanticRouterLayer(simple_model="flash-model", threshold_chars=30))
    
    # 3. Add Cost Optimizer (Limits budget)
    motor.add(CostOptimizerLayer(max_cost_usd=0.01, per_request=True))
    
    # 4. Add Logger to see the results
    motor.add(LoggerLayer())
    
    # Provider
    motor.use(MockProvider(response_text="I am processing your request safely."))

    # TEST 1: PII Redaction
    print("[Test 1] Sending PII (Email: test@example.com)...")
    await motor.prompt("My email is test@example.com, please help.")
    print("-" * 30)

    # TEST 2: Semantic Routing
    print("[Test 2] Sending a simple 'Hello' (Should trigger routing)...")
    await motor.prompt("Hello")
    print("-" * 30)

    # TEST 3: Budget Limit (MockProvider usually has 0 cost, but we can see the layer logic)
    print("[Test 3] Budget check...")
    # (In a real scenario with OpenAIProvider, this would block if budget exceeded)
    print("Budget logic is active in the background.")

if __name__ == "__main__":
    asyncio.run(main())
