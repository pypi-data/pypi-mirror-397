# tedx-flow

A lightweight task flow orchestration library for Python.

## Features

- **Zero Dependencies**: Uses only Python standard library
- **Thread-Safe**: Built-in synchronization for parallel execution
- **Simple API**: Easy to define and chain tasks
- **Streaming Support**: Real-time output as tasks complete
- **Dynamic Scheduling**: Tasks can schedule next tasks at runtime
- **Parallel Execution**: Independent tasks run concurrently

## Installation

```bash
pip install tedx-flow
```

## Quick Start

```python
from concurrent.futures import ThreadPoolExecutor
from tedx_flow import Flow, Context, NextTask, TaskOutput

# Define tasks
def fetch_data(ctx: Context) -> TaskOutput:
    data = {"items": [1, 2, 3, 4, 5]}
    return TaskOutput(output=data, next_tasks=[NextTask("process")])

def process(ctx: Context) -> TaskOutput:
    data = ctx.get("fetch_data")
    result = sum(data["items"])
    return TaskOutput(output=result)

# Create and run flow
with ThreadPoolExecutor(max_workers=4) as executor:
    flow = Flow(executor)
    flow.add_task("fetch_data", fetch_data)
    flow.add_task("process", process)
    
    results = flow.run("fetch_data")
    print(results)  # {"process": 15}
```

## Core Concepts

### Task

A task is the basic unit of a flow. Each task:
1. Receives a `Context` object (optionally with `inputs`)
2. Returns a `TaskOutput` containing output value and optional next tasks

```python
def my_task(ctx: Context, inputs: dict = None) -> TaskOutput:
    # Access previous task outputs
    previous_result = ctx.get("previous_task")
    
    # Access inputs passed via NextTask
    batch_size = inputs.get("batch_size", 10) if inputs else 10
    
    # Execute business logic
    result = do_something(previous_result, batch_size)
    
    # Return output and schedule next tasks
    return TaskOutput(
        output=result,
        next_tasks=[
            NextTask("next_task", inputs={"processed": True}),
            NextTask("parallel_task")  # Runs in parallel
        ]
    )
```

### Context

Context is a shared data container between tasks:
- `ctx.set(key, value)` - Store a value
- `ctx.get(key)` - Get a value (blocks until available)
- `ctx.to_dict()` - Export as dictionary

### TaskOutput

```python
# Terminal task (no next tasks)
TaskOutput(output="done")

# Chain to next task
TaskOutput(output=result, next_tasks=[NextTask("next_step")])

# Fan out to multiple tasks (parallel)
TaskOutput(output=result, next_tasks=[
    NextTask("branch_a"),
    NextTask("branch_b")
])
```

### NextTask

```python
# Simple scheduling
NextTask("task_name")

# With input parameters
NextTask("task_name", inputs={"key": "value"})

# Allow parallel instances of same task
NextTask("task_name", spawn_another=True)
```

## Streaming

Get real-time results as tasks complete:

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    flow = Flow(executor)
    flow.add_task("task_a", task_a)
    flow.add_task("task_b", task_b)
    
    for chunk in flow.stream("task_a"):
        print(f"Task {chunk.task_id} completed: {chunk.value}")
```

## Parallel Task Instances

Run multiple instances of the same task:

```python
def fan_out(ctx: Context) -> TaskOutput:
    return TaskOutput(
        output="started",
        next_tasks=[
            NextTask("worker", inputs={"id": 1}, spawn_another=True),
            NextTask("worker", inputs={"id": 2}, spawn_another=True),
            NextTask("worker", inputs={"id": 3}, spawn_another=True),
        ]
    )
```

## Error Handling

Exceptions in tasks are automatically propagated:

```python
try:
    results = flow.run("start_task")
except Exception as e:
    print(f"Flow execution failed: {e}")
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `Flow` | Main orchestration engine |
| `Context` | Shared state between tasks |
| `TaskOutput` | Task return type |
| `NextTask` | Specifies next task to run |
| `StreamChunk` | Streaming output container |
| `State` | Thread-safe value container |

### Flow Methods

| Method | Description |
|--------|-------------|
| `add_task(name, action)` | Register a task |
| `run(start_task_id, inputs)` | Execute flow synchronously |
| `stream(start_task_id, inputs)` | Execute with streaming output |
| `get_context()` | Get flow context |

## Use Cases

- **Data Processing Pipelines**: ETL, data cleaning, transformation
- **AI Workflows**: Multi-step LLM calls, RAG pipelines
- **Batch Processing**: Parallel sub-task processing
- **Business Processes**: Order processing, approval workflows

## License

MIT License
