import asyncio
import sys
import os
from rich.console import Console

sys.path.append(os.getcwd())

from velox.core.engine import Velox
from velox.providers.openai import OpenAIProvider
from velox.layers.advanced_dashboard import AdvancedDashboardLayer

console = Console()

async def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[bold yellow]No OPENAI_API_KEY found in env.[/bold yellow]")
        api_key = console.input("Enter OpenAI API Key to test: ")
    
    if not api_key:
        console.print("[red]No API Key provided. Exiting.[/red]")
        return

    motor = Velox()
    
    # Enable the "Pro" UI
    motor.add(AdvancedDashboardLayer())
    
    # Use Real OpenAI
    try:
        motor.use(OpenAIProvider(api_key=api_key, model="gpt-3.5-turbo"))
    except Exception as e:
        console.print(f"[red]Error initializing provider:[/red] {e}")
        return
    
    # Run
    await motor.prompt("Explain the theory of relativity in 2 sentences.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
