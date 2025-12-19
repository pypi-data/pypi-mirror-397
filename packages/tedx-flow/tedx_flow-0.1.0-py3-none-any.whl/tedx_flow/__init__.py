"""
tedx_flow - Lightweight Task Flow Orchestration Library

A simple, thread-safe task flow engine for orchestrating complex workflows.
Zero external dependencies - uses only Python standard library.

Example:
    from tedx_flow import Flow, Context, NextTask, TaskOutput
    from concurrent.futures import ThreadPoolExecutor

    def task_a(ctx: Context) -> TaskOutput:
        return TaskOutput(output="Hello", next_tasks=[NextTask("task_b")])

    def task_b(ctx: Context) -> TaskOutput:
        result = ctx.get("task_a")
        return TaskOutput(output=f"{result} World!")

    with ThreadPoolExecutor(max_workers=4) as executor:
        flow = Flow(executor)
        flow.add_task("task_a", task_a)
        flow.add_task("task_b", task_b)
        result = flow.run("task_a")
        print(result)  # {"task_b": "Hello World!"}

Features:
    - Zero Dependencies: Uses only Python standard library
    - Thread-Safe: Built-in synchronization
    - Simple API: Easy to define and chain tasks
    - Streaming Support: Real-time task results
    - Dynamic Scheduling: Runtime task decisions
    - Parallel Execution: Concurrent independent tasks
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .context import Context
from .flow import Flow, NextTask, StreamChunk, TaskOutput
from .state import State

__all__ = [
    "Context",
    "Flow",
    "NextTask",
    "StreamChunk",
    "TaskOutput",
    "State",
]
