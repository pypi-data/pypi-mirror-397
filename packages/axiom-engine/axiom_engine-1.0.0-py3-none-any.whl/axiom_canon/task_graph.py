from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TaskNode:
    """
    A single unit of work in the Task Graph.
    """
    id: str
    name: str
    description: str
    command: Optional[str] = None
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    retries: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300

@dataclass
class TaskDependency:
    """
    Dependency between tasks.
    """
    upstream_task_id: str
    downstream_task_id: str

@dataclass
class TaskGraph:
    """
    A Directed Acyclic Graph (DAG) of tasks.
    Produced by Tactical agents, consumed by the Task Executor.
    """
    id: str
    tasks: Dict[str, TaskNode] = field(default_factory=dict)
    dependencies: List[TaskDependency] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
