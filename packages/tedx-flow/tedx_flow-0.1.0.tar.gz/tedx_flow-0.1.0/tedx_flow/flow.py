"""
Flow engine for tedx_flow.

Provides the core Flow class for orchestrating task execution with
support for parallel execution, streaming, and dynamic task scheduling.
"""

import logging
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from inspect import signature
from queue import Queue
from threading import Lock
from typing import Any, Callable, Dict, Generator, List, Optional

from .context import Context
from .state import State

__ERROR__ = "__ERROR__"
__OUTPUT__ = "__OUTPUT__"
__HASH_SPLIT__ = "____"


@dataclass
class NextTask:
    """
    Represents a task scheduled to run next in the flow.

    Attributes:
        id: The unique identifier of the next task
        inputs: Dictionary of inputs to pass to the next task
        spawn_another: If True, allows parallel execution of same task
    
    Example:
        # Simple next task
        NextTask("process_data")
        
        # With inputs
        NextTask("process_data", inputs={"batch_size": 100})
        
        # Allow parallel instances
        NextTask("process_data", spawn_another=True)
    """
    id: str
    inputs: Optional[Dict[str, Any]] = None
    spawn_another: bool = False


@dataclass
class TaskOutput:
    """
    Output from a task execution.

    Attributes:
        output: The result value from the task
        next_tasks: List of tasks to schedule next (None = terminal task)
    
    Example:
        # Terminal task (no next tasks)
        TaskOutput(output="done")
        
        # Chain to next task
        TaskOutput(output=result, next_tasks=[NextTask("next_step")])
        
        # Fan out to multiple tasks
        TaskOutput(output=result, next_tasks=[
            NextTask("branch_a"),
            NextTask("branch_b")
        ])
    """
    output: Any
    next_tasks: Optional[List[NextTask]] = None


@dataclass
class Task:
    """Internal task representation."""
    id: str
    action: Callable[[Context], TaskOutput]


@dataclass
class StreamChunk:
    """
    A chunk of streaming output from a task.

    Attributes:
        task_id: The ID of the task that produced this chunk
        value: The output value
    """
    task_id: str
    value: Any


class Flow:
    """
    Task flow orchestration engine.
    
    Flow manages the execution of interconnected tasks, handling:
    - Parallel task execution via ThreadPoolExecutor
    - Task dependencies through Context
    - Dynamic task scheduling based on TaskOutput.next_tasks
    - Streaming output for real-time results
    - Error propagation and cleanup
    
    Example:
        from concurrent.futures import ThreadPoolExecutor
        
        def fetch_data(ctx: Context) -> TaskOutput:
            data = fetch_from_api()
            return TaskOutput(output=data, next_tasks=[NextTask("process")])
        
        def process(ctx: Context) -> TaskOutput:
            data = ctx.get("fetch_data")
            result = transform(data)
            return TaskOutput(output=result)
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            flow = Flow(executor)
            flow.add_task("fetch_data", fetch_data)
            flow.add_task("process", process)
            results = flow.run("fetch_data")
    """
    
    def __init__(
        self,
        thread_pool_executor: ThreadPoolExecutor,
        context: Optional[Context] = None,
    ):
        """
        Initialize a Flow instance.
        
        Args:
            thread_pool_executor: Executor for parallel task execution
            context: Optional pre-configured context (creates new if None)
        """
        self.tasks: Dict[str, Task] = {}
        self.active_tasks: set = set()
        self.context = context or Context()
        self.output_task_ids: set = set()
        self._executor = thread_pool_executor

        # Thread-safety locks
        self.active_tasks_lock = Lock()
        self.output_ids_lock = Lock()
        self.logger = logging.getLogger(__name__)

    def add_task(self, name: str, action: Callable[[Context], TaskOutput]):
        """
        Register a task with the flow.
        
        Args:
            name: Unique task identifier
            action: Task function that takes Context and returns TaskOutput
        """
        self.context.set_state(name, State.empty())
        self.tasks[name] = Task(name, action)
        self.logger.info(f"Added task '{name}'")

    def execute_task(
        self,
        action: Callable[[Context], TaskOutput],
        task: NextTask,
        task_queue: Queue,
        stream_queue: Optional[Queue] = None
    ):
        """
        Execute a single task.
        
        Args:
            action: The task function to execute
            task: NextTask containing task ID and inputs
            task_queue: Queue for scheduling subsequent tasks
            stream_queue: Optional queue for streaming output
        """
        self.logger.info(f"Starting execution of task '{task.id}'")

        try:
            # Check if action accepts inputs parameter
            sig = signature(action)
            if "inputs" in sig.parameters:
                result: TaskOutput = action(self.context, inputs=task.inputs)
            else:
                result: TaskOutput = action(self.context)

            # Set state to the output of the task
            self.context.set(task.id, result.output)

            # Push to stream queue if it exists
            if stream_queue is not None:
                stream_queue.put(StreamChunk(task.id, result.output))

            with self.active_tasks_lock:
                self.active_tasks.remove(task.id)
                self.logger.info(f"Completed execution of task '{task.id}'")

                # If no next tasks specified, this is an output task
                if not result.next_tasks or len(result.next_tasks) == 0:
                    self.logger.info(f"Task '{task.id}' completed as output node")
                    with self.output_ids_lock:
                        self.output_task_ids.add(task.id)
                        task_queue.put(NextTask(__OUTPUT__, None))
                else:
                    self.logger.debug(
                        f"Task '{task.id}' scheduling next tasks: {result.next_tasks}"
                    )

                    for next_task in result.next_tasks:
                        base_task_id = next_task.id.split(__HASH_SPLIT__)[0]
                        if base_task_id in self.tasks:
                            if next_task.id not in self.active_tasks:
                                self.active_tasks.add(next_task.id)
                                task_queue.put(NextTask(next_task.id, next_task.inputs))
                            elif next_task.spawn_another:
                                self.logger.info(
                                    f"Spawning another instance of task '{next_task.id}'"
                                )
                                task_id_with_hash = (
                                    next_task.id + __HASH_SPLIT__ + str(uuid.uuid4())[0:8]
                                )
                                self.active_tasks.add(task_id_with_hash)
                                task_queue.put(NextTask(task_id_with_hash, next_task.inputs))
                        else:
                            raise Exception(f"Task {next_task.id} not found")

        except Exception as e:
            self.context.set(
                __ERROR__, {"error": str(e), "traceback": traceback.format_exc()}
            )
            with self.active_tasks_lock:
                self.active_tasks.clear()

            task_queue.put(NextTask(__ERROR__, None))
            raise e

    def run(
        self, start_task_id: str, inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the flow starting from a specific task.
        
        This method blocks until all tasks complete and returns
        the outputs of all terminal tasks (tasks with no next_tasks).
        
        Args:
            start_task_id: ID of the task to start execution from
            inputs: Optional initial inputs to set in context
            
        Returns:
            Dictionary mapping output task IDs to their output values
            
        Raises:
            Exception: If any task fails during execution
        """
        self.logger.info(f"Starting flow run with initial task: {start_task_id}")
        
        task_queue: Queue = Queue()
        futures = set()
        
        self.active_tasks.add(start_task_id)
        task_queue.put(NextTask(start_task_id, inputs))

        if inputs:
            for key, value in inputs.items():
                self.context.set(key, value)

        # Main execution loop
        while True:
            next_task = task_queue.get()

            if next_task.id == __ERROR__:
                # Cancel all pending futures on error
                for f in futures:
                    f.cancel()

                err = self.context.get(__ERROR__)
                raise Exception(err)

            if next_task.id == __OUTPUT__:
                with self.active_tasks_lock:
                    if len(self.active_tasks) == 0:
                        break
                continue

            action = self.tasks[next_task.id.split(__HASH_SPLIT__)[0]].action

            future = self._executor.submit(
                self.execute_task, action, next_task, task_queue
            )
            futures.add(future)

        # Return values of the output nodes
        return {task_id: self.context.get(task_id) for task_id in self.output_task_ids}

    def stream(
        self, start_task_id: str, inputs: Optional[Dict[str, Any]] = None
    ) -> Generator[StreamChunk, None, None]:
        """
        Execute the flow with streaming output.
        
        Yields StreamChunk objects as each task completes, allowing
        real-time processing of intermediate results.
        
        Args:
            start_task_id: ID of the task to start execution from
            inputs: Optional initial inputs to set in context
            
        Yields:
            StreamChunk objects containing task_id and output value
        """
        task_queue: Queue = Queue()
        stream_queue: Queue = Queue()
        futures = set()

        self.active_tasks.add(start_task_id)
        task_queue.put(NextTask(start_task_id, inputs))

        if inputs:
            for key, value in inputs.items():
                self.context.set(key, value)

        self.context.set_stream(stream_queue)

        def run_engine():
            while True:
                next_task = task_queue.get()

                if next_task.id == __ERROR__:
                    for f in futures:
                        f.cancel()
                    stream_queue.put(StreamChunk(__ERROR__, None))
                    break

                if next_task.id == __OUTPUT__:
                    with self.active_tasks_lock:
                        if len(self.active_tasks) == 0:
                            stream_queue.put(StreamChunk(__OUTPUT__, None))
                            break
                    continue

                action = self.tasks[next_task.id.split(__HASH_SPLIT__)[0]].action

                future = self._executor.submit(
                    self.execute_task, action, next_task, task_queue, stream_queue
                )
                futures.add(future)

        self._executor.submit(run_engine)

        # Yield results from stream queue
        while True:
            stream_chunk: StreamChunk = stream_queue.get()
            if stream_chunk.task_id in (__OUTPUT__, __ERROR__):
                break
            yield stream_chunk

    def get_context(self) -> Context:
        """
        Get the flow's context.
        
        Returns:
            The Context instance used by this flow
        """
        return self.context
