from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time

class UsageMetrics(BaseModel):
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0

class Message(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class EventContext(BaseModel):
    """
    The state object that travels through the Velox pipeline.
    It holds the request, the accumulated metrics, and the final response.
    """
    # 1. Input State
    messages: List[Message]
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    
    # 2. Metadata (for routing/logging)
    session_id: str = Field(default_factory=lambda: str(time.time()))
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # 3. Output State (Populated by the Provider)
    response_content: Optional[str] = None
    
    # 4. Telemetry
    metrics: UsageMetrics = Field(default_factory=UsageMetrics)
    start_time: float = Field(default_factory=time.time)

    def set_response(self, content: str, usage: Optional[UsageMetrics] = None):
        self.response_content = content
        self.metrics.latency_ms = (time.time() - self.start_time) * 1000
        if usage:
            self.metrics.total_tokens = usage.total_tokens
            self.metrics.prompt_tokens = usage.prompt_tokens
            self.metrics.completion_tokens = usage.completion_tokens
            self.metrics.cost_usd += usage.cost_usd
