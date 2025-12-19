"""Tests for tedx_flow."""

import time
from concurrent.futures import ThreadPoolExecutor

import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tedx_flow import Context, Flow, NextTask, StreamChunk, TaskOutput


class TestContext:
    """Tests for Context class."""

    def test_set_and_get(self):
        ctx = Context()
        ctx.set("key", "value")
        assert ctx.get("key") == "value"

    def test_get_missing_key_raises(self):
        ctx = Context()
        with pytest.raises(Exception, match="Key .* not found"):
            ctx.get("missing")

    def test_to_dict(self):
        ctx = Context()
        ctx.set("a", 1)
        ctx.set("b", 2)
        result = ctx.to_dict()
        assert result["a"] == 1
        assert result["b"] == 2

    def test_from_dict(self):
        ctx = Context()
        ctx.from_dict({"x": 10, "y": 20})
        assert ctx.get("x") == 10
        assert ctx.get("y") == 20


class TestFlow:
    """Tests for Flow class."""

    def test_simple_flow(self):
        """Test a simple two-task flow."""
        def task_a(ctx: Context) -> TaskOutput:
            return TaskOutput(output="hello", next_tasks=[NextTask("task_b")])

        def task_b(ctx: Context) -> TaskOutput:
            result = ctx.get("task_a")
            return TaskOutput(output=f"{result} world")

        with ThreadPoolExecutor(max_workers=2) as executor:
            flow = Flow(executor)
            flow.add_task("task_a", task_a)
            flow.add_task("task_b", task_b)
            result = flow.run("task_a")

        assert result == {"task_b": "hello world"}

    def test_flow_with_inputs(self):
        """Test flow with initial inputs."""
        def task_a(ctx: Context, inputs: dict = None) -> TaskOutput:
            name = inputs.get("name", "unknown") if inputs else "unknown"
            return TaskOutput(output=f"Hello, {name}!")

        with ThreadPoolExecutor(max_workers=2) as executor:
            flow = Flow(executor)
            flow.add_task("task_a", task_a)
            result = flow.run("task_a", inputs={"name": "Alice"})

        assert result == {"task_a": "Hello, Alice!"}

    def test_parallel_tasks(self):
        """Test parallel task execution."""
        execution_order = []

        def task_start(ctx: Context) -> TaskOutput:
            execution_order.append("start")
            return TaskOutput(
                output="started",
                next_tasks=[NextTask("task_a"), NextTask("task_b")]
            )

        def task_a(ctx: Context) -> TaskOutput:
            time.sleep(0.1)
            execution_order.append("a")
            return TaskOutput(output="a_done")

        def task_b(ctx: Context) -> TaskOutput:
            time.sleep(0.1)
            execution_order.append("b")
            return TaskOutput(output="b_done")

        with ThreadPoolExecutor(max_workers=4) as executor:
            flow = Flow(executor)
            flow.add_task("task_start", task_start)
            flow.add_task("task_a", task_a)
            flow.add_task("task_b", task_b)
            result = flow.run("task_start")

        assert "task_a" in result
        assert "task_b" in result
        assert execution_order[0] == "start"

    def test_streaming(self):
        """Test streaming output."""
        def task_a(ctx: Context) -> TaskOutput:
            return TaskOutput(output="first", next_tasks=[NextTask("task_b")])

        def task_b(ctx: Context) -> TaskOutput:
            return TaskOutput(output="second")

        with ThreadPoolExecutor(max_workers=2) as executor:
            flow = Flow(executor)
            flow.add_task("task_a", task_a)
            flow.add_task("task_b", task_b)

            chunks = list(flow.stream("task_a"))

        assert len(chunks) == 2
        task_ids = {c.task_id for c in chunks}
        assert "task_a" in task_ids
        assert "task_b" in task_ids

    def test_spawn_another(self):
        """Test spawning multiple instances of same task."""
        results = []

        def task_start(ctx: Context) -> TaskOutput:
            return TaskOutput(
                output="started",
                next_tasks=[
                    NextTask("worker", inputs={"id": 1}, spawn_another=True),
                    NextTask("worker", inputs={"id": 2}, spawn_another=True),
                ]
            )

        def worker(ctx: Context, inputs: dict = None) -> TaskOutput:
            worker_id = inputs.get("id") if inputs else 0
            results.append(worker_id)
            return TaskOutput(output=f"worker_{worker_id}")

        with ThreadPoolExecutor(max_workers=4) as executor:
            flow = Flow(executor)
            flow.add_task("task_start", task_start)
            flow.add_task("worker", worker)
            flow.run("task_start")

        assert sorted(results) == [1, 2]

    def test_error_handling(self):
        """Test error propagation."""
        def failing_task(ctx: Context) -> TaskOutput:
            raise ValueError("Task failed!")

        with ThreadPoolExecutor(max_workers=2) as executor:
            flow = Flow(executor)
            flow.add_task("failing", failing_task)

            with pytest.raises(Exception):
                flow.run("failing")

    def test_get_context(self):
        """Test getting flow context."""
        with ThreadPoolExecutor(max_workers=2) as executor:
            ctx = Context()
            ctx.set("initial", "value")
            flow = Flow(executor, context=ctx)

            assert flow.get_context().get("initial") == "value"


class TestNextTask:
    """Tests for NextTask dataclass."""

    def test_defaults(self):
        task = NextTask("my_task")
        assert task.id == "my_task"
        assert task.inputs is None
        assert task.spawn_another is False

    def test_with_inputs(self):
        task = NextTask("my_task", inputs={"key": "value"})
        assert task.inputs == {"key": "value"}

    def test_spawn_another(self):
        task = NextTask("my_task", spawn_another=True)
        assert task.spawn_another is True


class TestTaskOutput:
    """Tests for TaskOutput dataclass."""

    def test_terminal_task(self):
        output = TaskOutput(output="result")
        assert output.output == "result"
        assert output.next_tasks is None

    def test_with_next_tasks(self):
        output = TaskOutput(
            output="result",
            next_tasks=[NextTask("next")]
        )
        assert len(output.next_tasks) == 1
        assert output.next_tasks[0].id == "next"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
