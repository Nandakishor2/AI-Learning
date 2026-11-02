"""
a2a_protocol.py
Agent-to-Agent (A2A) Communication Protocol Specification.
Defines AgentCard schemas, TaskLifecycle states, and standard message envelopes
for inter-agent delegation and synthesis.
"""

import uuid
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

class TaskState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class AgentCard:
    """Standard AgentCard advertising specialist capabilities and contracts."""
    agent_id: str
    name: str
    role: str
    description: str
    capabilities: List[str]
    input_contract: Dict[str, str]
    output_contract: Dict[str, str]

@dataclass
class A2AMessage:
    """Standard message envelope passed between collaborating agents."""
    task_id: str
    sender_id: str
    recipient_id: str
    task_type: str
    state: TaskState
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    parent_task_id: Optional[str] = None
    token_usage: int = 0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value
        return d

